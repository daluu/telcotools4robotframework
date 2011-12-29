#!/usr/bin/python
import re
from DTMFdetector import DTMFdetector

# Robot Framework test library for detecting DTMF digits from a wave audio file.

# From http://code.google.com/p/telcotools4robotframework/
# @author David Luu

# Using public domain DTMF library code from
# http://johnetherton.com/projects/pys60-dtmf-detector

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

class DetectDtmfFromFileLibrary:
	"""Test library for detecting DTMF digits from a wave audio file.
	
	Default supported & tested audio file formats are
	16-bit, mono, 8kHz, PCM encoding (default format)
	16-bit, mono, 16kHz, PCM encoding (doesn't work well)
	
	For other sample sizes, frequencies, and encoding formats, you will have to modify the library source code to support them. Library currently has parameters to set these other formats but ignores them as functionality not implemented.
	
	*NOTE:* If you try and supply a wave audio file w/ unsupported audio file format, library will likely return an error or unreliable results.
	
	Best suggestion for using audio files in other formats is to use converter to get them into supported format for DTMF detection. For command line/automation processing, suggest Sox - http://sox.sourceforge.net. Or use the SoxAudioConversionLibrary that's part of the telcotools4robotframework package.
	
	*Reference:*
	frequency (Hz) = 8000, 16000, 11025, 22050, 44100, etc.
	sample size, in bits = 8, 16
	channels = 1 for mono, 2 for stereo
	encoding = PCM, ADPCM, mu-Law, a-Law, etc.
	
	This test library is built upon public domain DTMF detection library from http://johnetherton.com/projects/pys60-dtmf-detector
	
	"""
	
	__version__ = '1.0'
	ROBOT_LIBRARY_SCOPE = 'GLOBAL'
	
	def __init__(self, pFrequency=8000, pDebugFlag=False, pSampleSize=16, pChannels=1, pEncoding="PCM"):
		self._frequency = pFrequency
		self._debugFlag = pDebugFlag
		# unused & unimplemented settings
		# but defined here in case
		# implemented in the future
		self._sampleSize = pSampleSize
		self._channels = pChannels
		self._encoding = pEncoding
		
		# init the DTMF detector with given settings
		self._detector = DTMFdetector(self._frequency,self._debugFlag)
		
	def get_dtmf_from(self, wavFile):
		"""Extract and return a string of DTMF digits from given wave audio file.
		
		Given wave file must be full absolute path, or otherwise relative path will be used. Recommend use of absolute paths.
		"""
		try:
			data = self._detector.getDTMFfromWAV(wavfile)
			print data
			return data
		except IOError, err:
			print "Failed to get DTMF from %s. %s" % (path, err)
	
	def detect_dtmf(self, wavFile, dtmfString):
		"""Detects whether given DTMF digits exist within given wave audio file, using exact match search.
		
		Returns true if match found, otherwise false.
		
		Given wave file must be full absolute path, or otherwise relative path will be used. Recommend use of absolute paths.
		"""
		try:
			data = self._detector.getDTMFfromWAV(wavfile)
			print "Searching for '%s' and found '%s'" % (dtmfString,data)
			fnd = data.find(dtmfString)
			if fnd == -1:
				print "DTMF string not found."
				return False
			else:
				return True
		except IOError, err:
			print "Failed to detect DTMF from %s. %s" % (wavFile, err)
	
	def detect_dtmf_regex(self, wavFile, dtmfStringPattern):
		"""Detects whether given DTMF digits exist within given wave audio file, using regular expressions.
		
		Returns true if match found, otherwise false.
		
		Given wave file must be full absolute path, or otherwise relative path will be used. Recommend use of absolute paths.
		"""
		try:
			data = self._detector.getDTMFfromWAV(wavfile)
			print "Searching for '%s' with regex and found '%s'" % (dtmfString,data)
			matchObj = re.match(dtmfStringPattern, data, re.S|re.I)
			if matchObj:
				return True
			else:
				print "DTMF string pattern not found."
				return False
		except IOError, err:
			print "Failed to detect DTMF with regular expression from %s. %s" % (wavFile, err)
	