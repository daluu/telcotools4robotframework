#!/usr/bin/env python
#
# Modified by David Luu, 2010.
# Modified pcapdiff source code to make Robot Framework test library version.

# Copyright (C) 2007 Electronic Frontier Foundation
# Written November 2007 by Seth Schoen <schoen@eff.org>
#   and Steven Lucy <slucy@parallactic.com>
# Thanks to Peter Eckersley <pde@eff.org> and Fyodor
# 
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 or version 3 of the
# License.
# 
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
# 
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.

# - requires pcapy Python module -- available at
#   http://oss.coresecurity.com/projects/pcapy.html and also packaged in many
#   free software distributions
# - only checks IPv4 packets

import pcapy, sys, binascii, re, getopt
from pcapdiff_helper import *

__all__ = ['pcap_diff', 'pcap_dump']

class PcapLibrary:
	
	"""Library with various pcap functions to assist with telecommunications and networking testing in Robot Framework.
	
	Functions currently include pcap diff and dumping PCAP content. Currently this library is a port of pcapdiff tool from Electronic Frontier Foundation.
	
	Requires pcapy Python module -- available at http://oss.coresecurity.com/projects/pcapy.html and also packaged in many free software distributions.
	
	Only checks IPv4 packets.
	
	Library (constructor) options:
	
	pVerbosity_level=n
	Increase verbosity level, or set to n.  Valid levels are 0 (default), 1, and 2. At verbosity level 0, pcapdiff will print only a summary table of the packets it processed.  At level 1, it will print out IP ident fields of interesting packets (dropped, forged, etc.).  At level 2, it will print out the actual packets (including payload) and lots of other information.
	
	pIgnore_tcp_checksum=1, 
	Do not ignore the TCP/UDP checksum when comparing packets.  Normally, TCP/UDP checksums are ignored because checksum offloading results in bad checksums on the sending side.  Use this option if you don't have (or have disabled) checksum offloading on both machines used to produce the pcap files, or if the pcap files were captured on another machine on the local network. *NOT FULLY IMPLEMENTED.*
		  
	pIgnore_timestamps=1, 
	Trust timestamps in pcap files.  With this option, pcapdiff looks at when each file begins and ends, and only compares the intersection of the two time intervals. *SEE pcapdiff README FILE.*
	
	pSkew_clocks=0, 
	Use this option if the two host clocks were not synchronized AND the first packet in both dump files is the same packet.  pcapdiff will subtract the difference between the timestamps on these two packets to find the clock skew and apply this difference to all other timestamps.  The purpose of this option is to reduce the amount of memory used by pcapdiff; it will never affect the output (except for printing the clock skew).
	"""
	
	__version__ = '0.1'
	ROBOT_LIBRARY_SCOPE = 'GLOBAL'
	
	def __init__(self, pVerbosity_level=0, pIgnore_tcp_checksum=1, pIgnore_timestamps=1, pSkew_clocks=0, pSkew_amount=0):
		self._verbosity_level = pVerbosity_level
		self._ignore_tcp_checksum = pIgnore_tcp_checksum
		self._ignore_timestamps = pIgnore_timestamps
		self._skew_clocks = pSkew_clocks
		self._skew_amount = pSkew_amount
		
	def pcap_diff(localPcap,localIp,remotePcap,remoteIp):
		"""Shows you the differences between two pcap dump files (such as those produced by tcpdump), with an eye towards counting and identifying forged and dropped packets.
		
		See pcapdiff README for more information.
		
		pcapdiff takes two pcap files (usually produced by running tcpdump on two different computers) and compares them to find any dropped and forged packets between the two machines, or that the network data transmission was successful (target machine pcap content is same as source machine).
		
		Required arguments are the filenames of the two pcap files and their associated IP addresses.
		
		Though pcapdiff uses "local" and "remote" to identify the two files, the processing should be symmetric -- it is only required that the "local" IP address is the IP address of the machine which produced the "local" pcap file (and similar for remote). Alternatively, one can assume local = source, remote = target/destination.
		
		Returns true if pcap files are different, otherwise false.
		"""
		
		try:
		    pcap_local = pcapy.open_offline(localPcap)
		    ip_local = localIp
		    pcap_remote = pcapy.open_offline(remotePcap)
		    ip_remote = remoteIp
		except:
		    print "Error opening pcap files or identifying IP addresses"
		    #sys.exit(1)
		    
		manifest = {}
		total = {}
		total['local'] = 0
		total['local_received'] = 0
		total['remote'] = 0
		total['remote_received'] = 0
		total['duplicates'] = 0
		
		re_ipfrom = re.compile('\nip_src: ([.\d]*)\n')
		re_ipto = re.compile('\nip_dest: ([.\d]*)\n')
		re_ipid = re.compile('\nip_ident: ([\d]*)\n')
		
		next = {}
		next['local']  = get_packet(pcap_local, 1)  #1 means ignore ip addresses
		next['remote'] = get_packet(pcap_remote, 1)
		
		if ['local'] == 0 or next['remote'] == 0:
		    raise Exception("ERROR: No packets in one or more files!")
		    #print "ERROR: No packets in one or more files!"
		    #sys.exit(2)
		
		last_ts_local  = tsp(next['local'])
		last_ts_remote = tsp(next['remote'])
		first_ts = max(last_ts_local, last_ts_remote)
		if skew_clocks:
		    skew_amount = last_ts_local - last_ts_remote
		    if v>=1: print "Clock skew:", skew_amount
		
		# now, find first real packet we care about:
		if not is_our_traffic(next['local']):
		    next['local']  = get_packet(pcap_local)
		if not is_our_traffic(next['remote']):
		    next['remote']  = get_packet(pcap_remote)
		
		# fast forward to after start time of later file
		if not ignore_timestamps:
		    while tsp(next['local']) < first_ts:
			next['local'] = get_packet(pcap_local)
		    while tsp(next['remote']) + skew_amount < first_ts:
			next['remote'] = get_packet(pcap_remote)
			
		############ MAIN LOOP
		
		while 1:
		    if next['local'] == 0 and next['remote'] == 0: break #it's all over
		
		    if next['local'] == 0: #we've reached the end of the local file
			#first, find the last timestamp (whether or not it's our traffic)
			next['local'] = get_packet(pcap_local, 1)
			if next['local'] != 0:
			    last_ts_local = tsp(next['local'])
			while not ignore_timestamps and next['local'] != 0:
			    next['local'] = get_packet(pcap_local, 1)
			    if next['local'] != 0:
				last_ts_local = tsp(next['local'])
			#then, parse remote till we hit that last timestamp
			while next['remote'] != 0 and\
			      (ignore_timestamps or tsp(next['remote']) + skew_amount < last_ts_local):
			    manifest_packet(next['remote'], 'remote')
			    next['remote'] = get_packet(pcap_remote)
			break #break the main loop
		
		    if next['remote'] == 0: #we've reached the end of the remote file
			#first, find the last timestamp (whether or not it's our traffic)
			next['remote'] = get_packet(pcap_remote, 1)
			if next['remote'] != 0:
			    last_ts_remote = tsp(next['remote'])
			while not ignore_timestamps and next['remote'] != 0:
			    next['remote'] = get_packet(pcap_remote, 1)
			    if next['remote'] != 0:
				last_ts_remote = tsp(next['remote'])
			#then, parse local till we hit that last timestamp
			while next['local'] != 0 and\
			      (ignore_timestamps or tsp(next['local']) < last_ts_remote):
			    manifest_packet(next['local'], 'local')
			    next['local'] = get_packet(pcap_local)
			break #break the main loop
		
		    #both files still being read: pick the earlier packet and manifest
		    if tsp(next['remote']) + skew_amount < tsp(next['local']):
			#print "Manifesting remote packet: %10d %10d %5d remote" % (tsp(next['remote']) + skew_amount, tsp(next['remote']), next['remote']['ip_ident'])
			last_ts_remote = tsp(next['remote'])
			manifest_packet(next['remote'], 'remote')
			next['remote'] = get_packet(pcap_remote)
		    else:
			#print "Manifesting local packet:  %10d            %5d" % (tsp(next['local']), next['local']['ip_ident'])
			last_ts_local = tsp(next['local'])
			manifest_packet(next['local'], 'local')
			next['local'] = get_packet(pcap_local)
		
		    #l = []
		    #for a in manifest.keys():
			#l.append(getid(a))
		    #l2 = map(lambda x: int(x), l)
		    #l2.sort()
		    #print l2
		
		############ END MAIN LOOP
		
		# finish up: make sure we deal with any packets that were in-flight
		# when we encountered the last timestamp on a file
		
		# XXX put code here
		
		if v >= 2: print "Parsed.  Local num of unique packets: %d, num of duplicate packets: %d" % (len(manifest.keys()), total['duplicates'])
		
		if v >= 2: print "Remote num of unmatching packets: %d" % len(manifest.keys())
		
		dropped_in = []
		dropped_out = []
		forged_in = []
		forged_out = []
		errors = []
		
		for p in manifest.keys():
		    mp = manifest[p]
		    if v >= 2: print '--------------'
		    ip_from = re_ipfrom.search(p).group(1)
		    ip_to = re_ipto.search(p).group(1)
		    if ip_from == ip_local and ip_to == ip_remote:
			if mp > 0:
			    if v >=2 : print "DROPPED: %d" % mp
			    dropped_out += [getid(p)] * abs(mp)
			elif mp < 0:
			    if v >= 2: print "!!! FORGED: %d" % mp
			    forged_out += [getid(p)] * abs(mp)
			else:
			    if v >= 2: print "ERROR"
			    errors += [getid(p)]
		    elif ip_from == ip_remote and ip_to == ip_local:
			if mp > 0:
			    if v >= 2: print "!!! FORGED: %d" % mp
			    forged_in += [getid(p)] * abs(mp)
			elif mp < 0:
			    if v >= 2: print "DROPPED: %d" % mp
			    dropped_in += [getid(p)] * abs(mp)
			else:
			    if v >= 2: print "ERROR"
			    errors += [getid(p)]
		    else:
			if v >= 2:
			    print "ERROR: ip addrs should have been dropped %d -> %d" % (ip_from, ip_to)
			errors += [1]
		    if v >= 2: print p
		
		if v >= 1:
		    print "Here are the IP identification fields for forged and dropped packets:"
		    print
		    print "list of  inbound forged  packets: ", ' '.join(forged_in)
		    print
		    print "list of outbound forged  packets: ", ' '.join(forged_out)
		    print
		    print "list of  inbound dropped packets: ", ' '.join(dropped_in)
		    print
		    print "list of outbound dropped packets: ", ' '.join(dropped_out)
		    print
		
		mystery = {}
		mystery['in'] = total['local'] - total['remote_received'] + len(forged_out) - len(dropped_out)
		mystery['out'] = total['remote'] - total['local_received'] + len(forged_in) - len(dropped_in)
		
		print "-------------"
		print "Packet counts"
		print "-------------"
		
		print "               inbound",\
		      "   outbound"
		print "sent:        %9d" % total['remote'],\
				 "  %9d" % total['local']
		print "received:    %9d" % total['local_received'],\
				 "  %9d" % total['remote_received']
		print "forged:      %9d" % len(forged_in),\
				 "  %9d" % len(forged_out)
		print "dropped:     %9d" % len(dropped_in),\
				 "  %9d" % len(dropped_out)
		if mystery['in'] != 0 or mystery['out'] != 0:
		    print "mystery:     %9d" % mystery['in'],\
			  "             %9d" % mystery['out']
		
		if len(errors): 
			print "\nERRORS: %d" % len(errors)
			return True
		else:
			return False
		
	def get_packet(a, ignore_ip=0):
	    '''
	    Gets next valid packet from pcapy reader a.
	    Valid means IPv4 and between our two hosts (unless ignore_ip == 1).
	    Returns a saved packet in dictionary form, or 0 for EOF.
	    '''
	    while 1:
		try:
		    packet = a.next()
		except pcapy.PcapError:
		    return 0
		spacket = parse_and_save(packet)
		try:
		    if (not ignore_ip) and (not is_our_traffic(spacket)):
			# not traffic between our two hosts, so continue
			continue
		except KeyError:
		    continue
		return spacket
	
	def is_our_traffic(spacket):
	    try:
		if ((spacket['ip_src'] == ip_local or spacket['ip_dest'] == ip_local) and\
		    (spacket['ip_src'] == ip_remote or spacket['ip_dest'] == ip_remote)):
		    return 1
		else: return 0
	    except:
		return 0
	
	def manifest_packet(spacket, file):
	    '''
	    Takes a saved packet (spacket) and applies it to the manifest.
	    You need to specify if this packet came from the local file
	    or the remote file by specifying the "file" argument as "local"
	    or "remote".  Returns a float of timestamp.
	    '''
	    s = packet_to_string(spacket, 1)
	    if file == 'remote':
		if s:
		    if spacket['ip_src'] == ip_remote:
			total['remote'] += 1
		    elif spacket['ip_dest'] == ip_remote:
			total['remote_received'] += 1
		    try:
			manifest[s] -= 1
			if manifest[s] == 0:
			    del(manifest[s])
		    except KeyError:
			manifest[s] = -1
	    elif file == 'local':
		if s:
		    if spacket['ip_src'] == ip_local:
			total['local'] += 1
		    elif spacket['ip_dest'] == ip_local:
			total['local_received'] += 1
		    try:
			manifest[s] += 1
			if manifest[s] == 0:
			    del(manifest[s])
			total['duplicates'] += 1 # no key error => duplicate packet
		    except KeyError: manifest[s] = 1
	    else: raise "Bad file, should be 'local' or 'remote': " % file
	    return float( spacket['timestamp'] )
	
	#shorthand for timestamp of a spacket
	def tsp(sp): return float( sp['timestamp'] )
		
	def getid(p): return re_ipid.search(p).groups(1)[0]
	
	def pcap_dump(pcapFile):
		"""Dumps out and returns packets from a pcap dump file with ether and ip header info and ip payload."""
		
		pcapContent = ""
		try:
		    pcap_local = pcapy.open_offline(pcapFile)
		except IndexError:
		    raise Exception("Failed to open pcap file: %s" % pcapFile)
		
		while 1:
		    try:
			packet = pcap_local.next()
		    except pcapy.PcapError:
			break
		    
		    pcapContent += "------------------\n%s" % packet_to_string(parse_and_save(packet))
		    
		    print pcapContent
		    return pcapContent
