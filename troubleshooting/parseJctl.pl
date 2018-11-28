#!/usr/bin/perl
# converts the output of journalctl --output verbose to a more human readable format
# 
# Marc Methot did something better, as usual
# https://github.com/mrVectorz/snips/blob/master/journal_text_converter.py
#

use Getopt::Long;
use Time::Local;
GetOptions ("date=s" => \$dateMatch, 'nogarbage' => \$nogarbage, 'magic' => \$magic);
@folders = @ARGV;
$excludeString = "os-collect-config No local metadata found|local-data not found\. Skipping|systemd (Stopping|Creating|Removing|Starting|Removed|Created) (slice )*user-[0-9]+\.slice\.|systemd (Stopped|Started) Session [0-9]+ of user [a-z0-9\-]+\.|systemd Starting Session [0-9]+ of user [a-z0-9\-]+\.|snmpd Connection from UDP|systemd-logind Removed session [0-9]+|sshd Accepted publickey for|systemd-logind New session [0-9]+ of user [a-z0-9\-]+\.|session opened for user [a-z0-9\-]+ by|sshd Received disconnect from|sshd pam_unix\(sshd:session\): session closed for user ";

open READ, $ARGV[0];
while (<READ>) {
 chomp;
 if (/^([a-z]{3}) ([0-9]{4}\-[0-9]{2}-[0-9]{2} [0-9]{2}:[0-9]{2}:[0-9]{2}\.[0-9]+)/i) {
  $tts = $2;
  if (%keys && (!$dateMatch || ($dateMatch && $ts =~ /$dateMatch/))) {
   if (!$nogarbage || ($nogarbage && "$keys{'SYSLOG_IDENTIFIER'} $keys{'MESSAGE'}" !~ /$excludeString/)) {
    $unit = ($keys{'_SYSTEMD_UNIT'} ? $keys{'_SYSTEMD_UNIT'} : ($keys{'SYSLOG_IDENTIFIER'} ? $keys{'SYSLOG_IDENTIFIER'} : $keys{'_COMM'}));
    print "$ts $keys{'_HOSTNAME'} $unit";
    for $k (keys %keys) {
     if ($k =~ /LIBVIRT/) {
      print " $k=$keys{$k}";
     }
    }
    print " $keys{'MESSAGE'}\n";
   }
   undef %keys;
  }
  $ts = $tts;
 } elsif ((!$dateMatch || ($dateMatch && $ts =~ /$dateMatch/)) && /[\s]+([^=]+)=(.*)/) {
  $key = $1;
  $val = $2;
  $keys{$key} = $val;
 }
}
close READ;
__END__
Tue 2017-10-24 10:37:50.315725 UTC [s=6bffb876a10048479266ab251fa82f13;i=524715a;b=0a163cddc55946f889e0c7d0d3b917e8;m=914ed6facb5;t=55c4887dc4ccd;x=98df4480dbf4c068]
    PRIORITY=6
    _BOOT_ID=0a163cddc55946f889e0c7d0d3b917e8
    _MACHINE_ID=1b52c42fb1eb47f4a8c09904d4735fc9
    _HOSTNAME=rdmewa22nce-h-pe4c7cn-013.rdmewa22.vzcpe.net
    _TRANSPORT=kernel
    SYSLOG_FACILITY=0
    SYSLOG_IDENTIFIER=kernel
    _KERNEL_SUBSYSTEM=pci
    _KERNEL_DEVICE=+pci:0000:06:00.0
    _UDEV_SYSNAME=0000:06:00.0
    MESSAGE=be2net 0000:06:00.0 eno49: Link is Down
    _SOURCE_MONOTONIC_TIMESTAMP=9986115138436
Tue 2017-10-24 10:37:50.694520 UTC [s=6bffb876a10048479266ab251fa82f13;i=524715b;b=0a163cddc55946f889e0c7d0d3b917e8;m=914ed7575b5;t=55c4887e215cd;x=8097ec6a12ce0792]

    _COMM=libvirtd
    _SELINUX_CONTEXT=system_u:system_r:virtd_t:s0-s0:c0.c1023
    MESSAGE=Failed to acquire pid file '/var/run/libvirtd.pid': Resource temporarily unavailable
    PRIORITY=3
    LIBVIRT_SOURCE=util.error
    CODE_FILE=util/virpidfile.c
    CODE_LINE=422
    CODE_FUNC=virPidFileAcquirePath
    LIBVIRT_DOMAIN=0
    LIBVIRT_CODE=38
    _SOURCE_REALTIME_TIMESTAMP=1523306261500043

