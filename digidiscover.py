#!/usr/bin/env python

# digidiscover.py
# Author: John Kelley  <FirstName> (at) <LastName> dot ca
# 10/24/08

import socket
from netifaces import interfaces, ifaddresses, AF_INET

def detectDigiDevice(timeout=1):
	"""This sends a UDP broadcast packet out over all available
	interfaces with an IPv4 broadcast address. It then detects
	and parses a response from Digi devices such as Connect ME
	and returns the Name/Version, MAC address and IP."""

	listenPort = 1181
	broadcastPort = 2362
	digiDiscoverPacket = "DIGI\x00\x01\x00\x06\xff\xff\xff\xff\xff\xff"
	
	#setup socket
	outsock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
	outsock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
	outsock.bind(('',listenPort))
	
	#send our discovery packet out over all interfaces
	for ifaceName in interfaces():
		try:
			for i in ifaddresses(ifaceName)[AF_INET]:
				outsock.sendto(digiDiscoverPacket, (i['broadcast'], broadcastPort))
		except:
			pass

	responses = []

	#wait for a response
	try:
		#setup the timeout
		outsock.settimeout(timeout)
		# until the socket timeout is raised or CTRL-C
		while True:
			#wait for data
			data, addr = outsock.recvfrom(2048)
		
			#process data
			if not data.startswith('DIGI'):
				return None
			mac = "%02X:%02X:%02X:%02X:%02X:%02X" % (ord(data[10]), ord(data[11]), ord(data[12]), ord(data[13]), ord(data[14]), ord(data[15]))
			len = ord(data[35])
			desc = data[36:(36+len)]+" "
			len2 = ord(data[36+len+7])
			desc += data[36+len+8: 36+len+8+len2]

			responses.append((addr[0], mac, desc))
	except socket.timeout:
		pass

	return responses

if __name__ == '__main__':
	for ip, mac, desc in detectDigiDevice():
		if ip is None:
			print "Unable to find a Digi device"
			exit()
		else:
			print "Found '%s' with MAC %s @ %s" % (desc, mac, ip)
