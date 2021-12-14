#!mitmdump -s

import mitmproxy.addonmanager
import mitmproxy.http
import mitmproxy.log
import mitmproxy.tcp
import mitmproxy.websocket
from mitmproxy import ctx
import json
import gzip
from datetime import datetime

class BytesDump(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, bytes):
            obj = unbyte(obj)
        return obj

def keys_string(d):
    rval = {}
    if not isinstance(d, dict):
        if isinstance(d,(tuple,list,set)):
            v = [keys_string(x) for x in d]
            return v
        else:
            return d

    for k,v in d.items():
        if isinstance(k,bytes):
            k = k.decode()
        if isinstance(v,dict):
            v = keys_string(v)
        elif isinstance(v,(tuple,list,set)):
            v = [keys_string(x) for x in v]
        else:
            try:
              v = keys_string(v.__dict__)
            except:
              v = v
        rval[k] = v
    return rval


def unbyte(obj):
    try:
        string = obj.decode()
    except UnicodeDecodeError:
        try:
            string = gzip.decompress(obj).decode()
        except gzip.BadGzipFile:
            string = obj
    return string[:128]
 
def dump_json(obj):
    return json.dumps(keys_string(obj), cls=BytesDump)
def filter_headers(head):
    if isinstance(head, str):
        return head
    fields = dict(head.__dict__.get('fields'))
    remove_keys = ['Host', 'Connection', 'accept-language', 'User-Agent', 'Origin', 'X-Requested-With', 'Referer', 'Accept-Encoding']
    for key in remove_keys:
        fields.pop(key, None)
    return fields

class SniffWebSocket:
    def __init__(self):
        pass
    def load(self, loader):
        ctx.options.listen_port = 8082

    def request(self, flow):
        ctx.log.info(f"REQUEST: {datetime.now()} {flow.type} {flow.request.method} {flow.request.url}")
        ctx.log.info(f"  REQUEST {datetime.now()} HEADERS: {filter_headers(flow.request.headers)}")
        ctx.log.info(f"  REQUEST {datetime.now()} CONTENT: {unbyte(flow.request.content)}")
        return
    def response(self, flow):
        ctx.log.info(f"RESPONSE: {datetime.now()} {flow.type} {flow.request.method} {flow.request.url}")
        r_data = flow.response.data
        headers = filter_headers(r_data.headers)
        ctx.log.info(f"  RESPONSE {datetime.now()} HEADERS: {headers}")
        ctx.log.info(f"  RESPONSE {datetime.now()} CONTENT: {unbyte(r_data.content)}")
        return

    def websocket_handshake(self, flow: mitmproxy.http.HTTPFlow):
        ctx.log.info(f"WEBSOCKET {datetime.now()} HANDSHAKE: {flow.type} {flow.request.method} {flow.request.url}")
        for flow_msg in flow.websocket.messages:
            direction = "RECV"
            if flow_msg.from_client:
                direction = "SENT"
            packet = flow_msg.content
            msg = f"WEBSOCKET {datetime.now()} HANDSHAKE MSG: {direction} {flow_msg.type}: {packet.decode('ascii')}"
            if flow_msg.dropped:
                ctx.log.error(f"  DROPPED: {msg}")
            else:
                ctx.log.info(f"  {msg}")



    def websocket_start(self, flow):
        ctx.log.info(f"WEBSOCKET {datetime.now()} START: {flow.type} {flow.request.method} {flow.request.url}")
        for flow_msg in flow.websocket.messages:
            direction = "RECV"
            if flow_msg.from_client:
                direction = "SENT"
            packet = flow_msg.content
            msg = f"WEBSOCKET {datetime.now()} START MSG: {direction} {flow_msg.type}: {packet.decode('ascii')}"
            if flow_msg.dropped:
                ctx.log.error(f"  DROPPED: {msg}")
            else:
                ctx.log.info(f"  {msg}")

    def websocket_message(self, flow):
        if not hasattr(flow, "websocket"):
            return
        ctx.log.info(f"WEBSOCKET: {datetime.now()} {flow.type} {flow.request.method} {flow.request.url}")
        for flow_msg in flow.websocket.messages:
            direction = "RECV"
            if flow_msg.from_client:
                direction = "SENT"
            packet = flow_msg.content
            msg = f"WEBSOCKET {datetime.now()} MSG: {direction} {flow_msg.type}: {packet.decode('ascii')}"
            if flow_msg.dropped:
                ctx.log.error(f"  DROPPED: {msg}")
            else:
                ctx.log.info(f"  {msg}")

    def websocket_error(self, flow):
        """
            A websocket connection has had an error.
        """

    def websocket_end(self, flow):
        """
            A websocket connection has ended.
        """

addons = [
    SniffWebSocket()
]
