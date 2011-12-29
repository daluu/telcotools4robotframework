#!/usr/bin/env python
#
# pcapdiff_helper: helper functions for pcapdiff.py
#
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
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301, USA.

import pcapy, sys, binascii

def print_saved_packet(spacket):
    '''
    Print out a packet saved with parse_and_save
    '''

    s = packet_to_string(spacket)
    if s:
	print '------------'
	print s

def packet_to_string(spacket, hidefields=0):
    '''
    Take a saved packet, dump out a string.
    Optional argument tells it to hide fields that might change between
    two hosts, e.g. ip_ttl
    '''

    s = '' # to be returned

    fields = 'timestamp eth_type eth_dest eth_src ip_version ip_header_length ip_tos ip_total_length ip_ident ip_flags_plus_offset ip_ttl ip_protocol ip_header_checksum ip_src ip_dest ip_options ip_payload_length ip_payload_data'.split(' ')

    hiddenfields = 'timestamp eth_type eth_dest eth_src ip_tos ip_ttl ip_header_checksum'.split(' ')

    if hidefields and spacket['eth_type'] == '(not IPv4)':
	return

    for field in fields:
	try:
	    if spacket.has_key(field) and not (hidefields and field in hiddenfields):
		if field == 'ip_payload_data':
		    s += field + ": " + str(spacket[field]).encode("string_escape") + "\n"
		else:
		    s += field + ": " + str(spacket[field]) + "\n"
	except KeyError:
	    pass

    return s

def parse_and_save(dump_packet, ignore_tcp_checksum = 1):
    '''
    Parse a pcap file and return a dictionary
    '''

    spacket = {}
    spacket['timestamp'] = "%d.%06d" % (dump_packet[0].getts()[0], dump_packet[0].getts()[1])

    packet = dump_packet[1]
    if ord(packet[12]) != 8 or ord(packet[13]) != 0:
	spacket['eth_type'] = '(not IPv4)'
	return spacket

    spacket['eth_type'] = "%02x%02x" % (ord(packet[12]), ord(packet[13]))

    spacket['eth_dest'] = binascii.hexlify(packet[0:6])
    spacket['eth_src'] = binascii.hexlify(packet[6:12])

    ip_packet = packet[14:]
    spacket['ip_version'] = binascii.hexlify(ip_packet[0])[0]
    if spacket['ip_version'] != '4':
	spacket['eth_type'] = '(not IPv4)'
	return spacket

    spacket['ip_header_length'] = binascii.hexlify(ip_packet[0])[1]
    spacket['ip_tos'] = binascii.hexlify(ip_packet[1])
    spacket['ip_total_length'] = 256*ord(ip_packet[2])+ord(ip_packet[3])
    spacket['ip_ident'] = 256*ord(ip_packet[4])+ord(ip_packet[5])
    spacket['ip_flags_plus_offset'] = binascii.hexlify(ip_packet[6:8])
    spacket['ip_ttl'] = ord(ip_packet[8])
    spacket['ip_protocol'] = ord(ip_packet[9])
    spacket['ip_header_checksum'] = binascii.hexlify(ip_packet[10:12])
    spacket['ip_src'] = "%d.%d.%d.%d" % tuple(map(ord,(ip_packet[12:16])))
    spacket['ip_dest'] = "%d.%d.%d.%d" % tuple(map(ord,(ip_packet[16:20])))
    header_len = 4*(ord(ip_packet[0]) & 0xF) # in bytes
    spacket['ip_options'] = binascii.hexlify(ip_packet[20:header_len])
    #payload = ip_packet[header_len:] # also in bytes
    if ignore_tcp_checksum and spacket['ip_protocol'] == 0x06:
	#ignore TCP checksums because of offloading
	payload = ip_packet[header_len:header_len+16] +\
	    '\0\0' + ip_packet[header_len+18:spacket['ip_total_length']] # also in bytes
    elif ignore_tcp_checksum and spacket['ip_protocol'] == 0x11:
	#ignore UDP checksums because of offloading
	payload = ip_packet[header_len:header_len+4] +\
	    '\0\0' + ip_packet[header_len+6:spacket['ip_total_length']] # also in bytes
    else:
	payload = ip_packet[header_len:spacket['ip_total_length']] # also in bytes

    spacket['ip_payload_length'] = len(payload)
    spacket['ip_payload_data'] = payload

    return spacket
