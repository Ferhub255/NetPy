# coding=utf8
# the above tag defines encoding for this document and is for Python 2.x compatibility

import re

regex = r"Cisco.+Software\s\((?P<software>\S+)\).+Version\s(?P<model>\S+),?(\W+.+){20}\W.+mail.+\W+(?P<email>.+).(\W+.+){2}\.\W.+ID\s(?P<Procesor_id>\S+)\W*(\W+.+){10}?register\s\S+\s(?P<regiester>\S+)\W*"

test_str = ("Cisco IOS Software, IOSv Software (VIOS-ADVENTERPRISEK9-M), Version 15.6(2)T, RELEASE SOFTWARE (fc2)\n"
	"Technical Support: http://www.cisco.com/techsupport\n"
	"Copyright (c) 1986-2016 by Cisco Systems, Inc.\n"
	"Compiled Tue 22-Mar-16 16:19 by prod_rel_team\n\n\n"
	"ROM: Bootstrap program is IOSv\n\n"
	"R1 uptime is 24 minutes\n"
	"System returned to ROM by reload\n"
	"System image file is \"flash0:/vios-adventerprisek9-m\"\n"
	"Last reload reason: Unknown reason\n\n\n\n"
	"This product contains cryptographic features and is subject to United\n"
	"States and local country laws governing import, export, transfer and\n"
	"use. Delivery of Cisco cryptographic products does not imply\n"
	"third-party authority to import, export, distribute or use encryption.\n"
	"Importers, exporters, distributors and users are responsible for\n"
	"compliance with U.S. and local country laws. By using this product you\n"
	"agree to comply with applicable laws and regulations. If you are unable\n"
	"to comply with U.S. and local laws, return this product immediately.\n\n"
	"A summary of U.S. laws governing Cisco cryptographic products may be found at:\n"
	"http://www.cisco.com/wwl/export/crypto/tool/stqrg.html\n\n"
	"If you require further assistance please contact us by sending email to\n"
	"export@cisco.com.\n\n"
	"Cisco IOSv (revision 1.0) with  with 460033K/62464K bytes of memory.\n"
	"Processor board ID 99XMUBT2L27OTWW9T6S68\n"
	"4 Gigabit Ethernet interfaces\n"
	"DRAM configuration is 72 bits wide with parity disabled.\n"
	"256K bytes of non-volatile configuration memory.\n"
	"2097152K bytes of ATA System CompactFlash 0 (Read/Write)\n"
	"0K bytes of ATA CompactFlash 1 (Read/Write)\n"
	"1024K bytes of ATA CompactFlash 2 (Read/Write)\n"
	"0K bytes of ATA CompactFlash 3 (Read/Write)\n\n\n\n"
	"Configuration register is 0x0\n")

matches = re.finditer(regex, test_str, re.MULTILINE)

for matchNum, match in enumerate(matches, start=1):
    
    print ("Match {matchNum} was found at {start}-{end}: {match}".format(matchNum = matchNum, start = match.start(), end = match.end(), match = match.group()))
    
    for groupNum in range(0, len(match.groups())):
        groupNum = groupNum + 1
        
        print ("Group {groupNum} found at {start}-{end}: {group}".format(groupNum = groupNum, start = match.start(groupNum), end = match.end(groupNum), group = match.group(groupNum)))

# Note: for Python 2.7 compatibility, use ur"" to prefix the regex and u"" to prefix the test string and substitution.