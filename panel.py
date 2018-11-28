#!/usr/bin/env python
#
# Incomplete script to manage  Bosch alarm panel B5512v2
#
# I don't have that panel anymore, so I can't  maintain it anymore
#
# It's my first python script, it's not beautiful.
# 
# Author: David Vallee Delisle <david@valleedelisle.com>
import socket, ssl, re, logging
import getopt, sys, json
import select, struct

# Alarm Panel settings
HOST, PORT, PASSCODE = '192.168.1.50', 7700, "Bosch_Auto"

# Let's configure the logging here
logging.basicConfig(level="DEBUG",
                    format='%(asctime)s %(levelname)s %(message)s',
                    datefmt='%Y-%m-%d %H:%M:%S',
                    filename='/srv/openhab2-logs/bosch-panel.log',
                    filemode='w')
console = logging.StreamHandler()
logging.getLogger('').addHandler(console)
formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
console.setFormatter(formatter)

# List of commands reference that can be sent to the Bosch Panel
cmdList = {
 'WhatAreYou': '01',
 'PasscodeAndUserTypeCheck': '0601',
 'RequestTextHistoryEvents': '16',
 'RequestRawHistoryEvents': '15',
 'ResetSensors': '18',
 'PanelCapacities': '1F',
 'RequestUser': '40',
 'RequestAlarmMemoryPriorities': '21',
 'RequestAlarmAreasByPriority': '22',
 'SilenceBells': '19',
 'TrySilenceBells': '19',
 'RequestConfiguredAreas': '24',
 'RequestAreaStatus': '26',
 'ArmPanelAreas': '27',
 'RequestAreasNotReadyToArm': '28',
 'RequestAreaText': '29',
 'RequestConfiguredDoors': '2B',
 'RequestDoorStatus': '2C',
 'SetDoorState': '2D',
 'RequestDoorText': '2E',
 'RequestConfiguredOutputs': '30',
 'RequestOutputStatus': '31',
 'SetOutputState': '32',
 'RequestOutputText': '33',
 'RequestConfiguredPoints': '35',
 'RequestPointsInArea': '36',
 'RequestFaultedPoints': '37',
 'RequestPointStatus': '38',
 'RequestBypassedPoints': '39',
 'BypassPoints': '3A',
 'UnbypassPoints': '3B',
 'RequestPointText': '3C'
}

# This is the arming commands
armCmdList = {
 "Disarm": "01",
 "ArmInstant": "02",
 "ArmDelayed": "03",
 "StayInstant": "04",
 "Stay": "05",
 "Force": "06"
}


# When return codes is FDXX, this is the correspondance with FD
NAK = {
 "00": "Non-specific error",
 "01": "Checksum failure (UDP connections only)",
 "02": "Invalid size / length",
 "03": "Invalid command",
 "04": "Invalid interface state",
 "05": "Data out of range",
 "06": "No authority",
 "07": "Unsupported command",
 "08": "Cannot arm panel",
 "09": "Invalid Remote ID",
 "0A": "Invalid License",
 "0B": "Invalid Magic Number",
 "0C": "Expired License",
 "0D": "Expired Magic Number",
 "0E": "Unsupported Format Version",
 "20": "Execution Function No Errors",
 "21": "Execution Function Invalid Area",
 "22": "Execution Function Invalid Command",
 "23": "Execution Function Not Authenticated",
 "24": "Execution Function Invalid User",
 "40": "Execution Function Parameter Incorrect",
 "41": "Execution Function Sequence Wrong",
 "42": "Execution Function Invalid Configuration Request",
 "43": "Execution Function Invalid Size",
 "44": "Execution Function Time Out",
 "E0": "No RF device with that RFID",
 "E1": "Bad RFID. Not proper format",
 "E2": "Too many RF devices for this panel",
 "E3": "Duplicate RFID",
 "E4": "Duplicate access card",
 "E5": "Bad access card data",
 "E6": "Bad language choice",
 "E7": "Bad supervision mode selection",
 "E8": "Bad enable/disable choice",
 "E9": "Bad Month",
 "EA": "Bad Day",
 "EB": "Bad Hour",
 "EC": "Bad Minute",
 "ED": "Bad Time edit choice",
 "EF": "Bad Remote Enable"
}


# Let's define global variables here
execCmd = None
rawCmd = None
armCmd = None
execTarget = None
getAreas = None
getPoints = None
getOutputs = None
# Default loglevel while coding
logLevel = "DEBUG"
skip = 0

# Some classes
class Areas:
    def __init__(self, number, active=0, status=0, text="Unknown"):
        self.number = number
        self.active = active
        self.status = status
        self.text = text

class Outputs:
    def __init__(self, number, active=0, status=0, text="Unknown"):
        self.number = number
        self.active = active
        self.status = status
        self.text = text

class Points:
    def __init__(self, number, active=0, status=0, text="Unknown"):
        self.number = number
        self.active = active
        self.status = status
        self.text = text

panelObjects = { 
    "area": {
        'className': Areas,
        'items': [],
        'statusName': {
                "00": "Unknown",
                "01": "All On",
                "02": "Part On instant",
                "03": "Part On Delay",
                "04": "Disarmed",
                "05": "All On Entry Delay",
                "06": "Part On Entry Delay",
                "07": "All On Exit Delay",
                "08": "Part On Exit Delay",
                "09": "All On Instant Armed"
        }
    }, 
    "output": {
        'className': Outputs,
        'items': []
    }, 
    "point": {
        'className': Points,
        'items': [],
        'statusName': {
                "00": "Unassigned",
                "01": "Short",
                "02": "Open",
                "03": "Normal",
                "04": "Missing"
         }
    }
}

# Help me function
def usage():
    print sys.argv[0],"--log=[INFO,DEBUG,ERROR] --arm=[arm mode] --raw=[raw hex string] --cmd=[cmdName] --target=[targetName] --getOutputs --getPoints --getAreas"
    print "\nArmModes:"
    for k in armCmdList:
        print "\t",k," => ", armCmdList[k]
    print "\nCommands:"
    for k in cmdList:
        print "\t",k," => ", cmdList[k]
    sys.exit()

# Get the arguments from the command line
def main():
    global execCmd
    global execTarget
    global rawCmd
    global armCmd
    global getAreas
    global getPoints
    global getOutputs
    global logLevel
    try:
        opts, args = getopt.getopt(sys.argv[1:],'l:c:ht:r:a:', ["help", "log=", "arm=", "raw=", "cmd=", "target=", "getAreas","getPoints","getOutputs"])
    except getopt.GetoptError as err:
        print str(err) 
        usage()
        sys.exit(2)
    for o, a in opts:
        if o in ("--raw","-r"):
            rawCmd = a
        elif o in ("--log","-l"):
            if a in ['INFO','DEBUG','ERROR','WARNING']:
                logLevel = a
            else:
                logging.error("Invalid log level: %s",a)
                usage()
        elif o in ("--arm","-a"):
            if a in armCmdList:
                armCmd = a
            else:
                logging.error("Invalid arm command: %s",a)
                usage()
        elif o in ("--cmd","-c"):
            if a in cmdList:
                execCmd = a
            else:
                logging.error("Invalid command: %s",a)
                usage()
        elif o in ("--target","-t"):
            execTarget = a
        elif o in ("--getAreas"):
            getAreas = True
        elif o in ("--getPoints"):
            getPoints = True
        elif o in ("--getOutputs"):
            getOutputs = True
        elif o in ("-h", "--help"):
            usage()
            sys.exit()
        else:
            assert False, "unhandled option"

if __name__ == "__main__":
    main()

# Let's define logLevel
console.setLevel(logLevel)

# Some helper function
def hEmpty(v):
    if v == None:
        return True
def hStatusName(itype,status):
        if "statusName" in panelObjects[itype]:
                return panelObjects[itype]["statusName"][status]
        else:
                return status;
def hBitMask(bit):
    return bin(int(bit, 16))[2:].zfill(4)

# Here we connect to the panel
def connectPanel():
    logging.info("Logging into the panel...")
    logging.debug("Connecting to %s:%s",HOST,PORT)
    context = ssl.SSLContext(ssl.PROTOCOL_TLSv1)
    context.verify_mode = ssl.CERT_NONE
    context.check_hostname = False
    context.options |= ssl.OP_NO_SSLv3
    context.options |= ssl.OP_NO_SSLv2
    context.options |= ssl.OP_NO_COMPRESSION
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(5)
    wrappedSocket = context.wrap_socket(sock, do_handshake_on_connect=True)
    wrappedSocket.connect((HOST, PORT))
    wrappedSocket.setblocking(1)
    return wrappedSocket

# Function to send packets
def sendPacket(data,nolog=None,noWrap=None):
    size = len(data) / 2
    size = "%0.2X" % size
    if noWrap == None:
        packet = "01" + size + str(data)
    else:
        packet = str(data)
    if hEmpty(nolog):
        packetShow = ':'.join(packet[i:i+2] for i in range(0, len(packet), 2))
        logging.debug("Packet: %s Data: %s Size: %s",packetShow,data,size)

    xb=""
    bits = re.findall('..',packet)
    for b in bits:
        xb +=chr(int(b,16))
    if hEmpty(nolog):
        logging.debug("Sending bytes: %s", xb)
    sent = socket.send(xb)
    if hEmpty(nolog):
        logging.debug("Bytes sent: %s", sent)

# Function to snif the socket
def receivePacket(length,nolog=None,skip=0):
    if hEmpty(nolog):
        logging.debug("Receiving %i bits",length)
    rcvd = socket.recv(length)
    if hEmpty(nolog):
        logging.debug("Received %i bits: %s",length,rcvd)
    if rcvd == None:
        logging.error("No response")
        #return False
    else:
        bits = re.findall('.',rcvd)
        logging.debug("Readable bits: %s",bits)
        if "%0.2X" % ord(bits[2]) == "FD":
            logging.error("NAK Error: %s", NAK["%0.2X" % ord(bits[3])])
        bits = bits[2+skip:]
        xb = ""
        for b in bits:
            xb += "%0.2X" % ord(b)
        if hEmpty(nolog):
            logging.debug("Converting hex %s: %s",xb,xb.decode("hex"))
    return xb

# Authentication function
def authorizePasscode():
    bits = re.findall('..',PASSCODE)
    xp = ""
    for p in bits:
        xp += p.encode("HEX").zfill(2).upper()
    passcode = "0601" + xp + "00"
    sendPacket(passcode,True)
    authStatus = receivePacket(4096,True)
    auths = re.findall('..',authStatus)
    if auths[0] == "FE":
        if auths[1] == "01":
            logging.debug("Authentication successfull")
        elif auths[1] == "00":
            logging.error("Authentication failed: Passcode is not authorized")
            sys.exit()
        elif auths[1] == "02":
            logging.error("Authentication failed: No more connection possible")
            sys.exit()
        else:
            logging.error("Authentication failed: Unknown error: %s",authStatus)
            sys.exit()
    elif auths[0] == "FD":
        logging.error("Authentication failed: NAK with errorcode: %s", authStatus)
        sys.exit()
    elif auths[0] == "FC":
        logging.error("Authentication failed: ACK'd, but error: continue: %s", authStatus)
    else:
        logging.error("Authentication failed: Unknown error")
        sys.exit()

# Returns the status of an item
def getItemStatus(itype,item):
    logging.debug("Getting status for %s %s",itype,item)
    sendPacket(cmdList['Request'+itype.title()+'Status'] + item)
    skip = 0 if itype == "output" else 3
    rl = receivePacket(4096,None,skip)
    if itype == "output":
        bits = bin(int(rl,16))
    else:
        bits = 0
    print '{0}{1}={2}'.format(itype.title(),item,hStatusName(itype,rl))
    logging.info("%s %s is currently in mode %s %s",itype.title(),int(item),bits,hStatusName(itype,rl))
    return rl

# Returns the text of an item
def getItemText(itype,item):
    itemId = item
    if itype == "output":
        itemId = "%0.2X" % (int(item) + 252)
    logging.debug("Getting text for %s %s",itype,item)
    data = cmdList['Request'+itype.title()+'Text'] + itemId + "00"
    sendPacket(data)
    rl = receivePacket(4096,None,1)
    logging.info("%s %s Name: %s",itype.title(),int(item),rl.decode("hex"))
    return rl.decode("hex")

# Getting infos on items
def getItemInfo(itype):
    sendPacket(cmdList['RequestConfigured'+itype.title()+'s'])
    rl = receivePacket(4096,None,1)
    itemList = re.findall('.',hBitMask(rl))
    items = []
    for i,j in enumerate(itemList):
        itemNum = str(i + 1)
        itemId = itemNum.zfill(4)
        if int(j) == 1:
            itemText = getItemText(itype,itemId)
            itemStatus = hStatusName(itype,getItemStatus(itype,itemId))
        else:
            itemStatus = 0
            itemText = "Disabled"
    items.append(panelObjects[itype]['className'](itemNum,int(j),itemStatus,itemText[:-1]))
    panelObjects[itype]['items'] = json.dumps([ob.__dict__ for ob in items])
    return items

# Arm an area
def setArmArea(area,armCmd):
    com = cmdList['ArmPanelAreas'] + armCmdList[armCmd]
    i=0
    mask = ""
    areaBits = ""
    while i <= 8:
        i += 1
        mask += "1" if int(i) == int(area) else "0"
    for byte in re.findall('....',mask):
        areaBits += "%0.1X" % int(byte,2)
    com += areaBits
    sendPacket(com)
    rl = receivePacket(4096)
    if rl == "FC00":
        logging.info("Area %s is now in mode %s",area,armCmd)
        return True
    else:
        logging.error("Error setting area %s in mode %s: %s",area,armCmd,rl)
        return False

# Connecting and authenticating
socket = connectPanel()
authorizePasscode()

if getAreas == True:
    getItemInfo('area')
elif getPoints == True:
    getItemInfo('point')
elif getOutputs == True:
    getItemInfo('output')
elif armCmd != None:
    setArmArea(execTarget,armCmd)
elif (execCmd != None and cmdList[execCmd]) or rawCmd != None:
    # If we send a raw command, we don't want to prepend the size and 01
    noWrap = None

    # Take the command from the list
    if rawCmd == None:
        com = cmdList[execCmd]
    # If we have a target (raw) this is appended here
    if execTarget != None:
        com += execTarget
    # Raw command from the Lug logs
    elif rawCmd != None:
        com = rawCmd
        skip = 0
        noWrap = True
    # Here we send the packet in the tube
    sendPacket(com,None,noWrap)
    rl = receivePacket(4096,None,skip)
    logging.info("Response: %s",rl)
else:
    logging.error("Command unknown: %s", execCmd)

socket.close()
