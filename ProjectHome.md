# Overview #

A collection of telecom related test libraries (or resource files) for use with [Robot Framework](http://www.robotframework.org). This collection is intended to provide a user-friendly set of tools for use with [Robot Framework](http://www.robotframework.org) to do telecom based testing, an industry that so far has not catered to non-developer user-base.

**NOTE:** consider the code offered here of Alpha quality, they're not production ready. With the eyebeam library being most complete (Beta). Not all the tools in the collection are code complete, I've not had time to come back to this after leaving my job in telecom industry.

The tool collection comprises of the following

## Tool Collection ##

  * sipp resource file (to run [SIPP](http://sipp.sourceforge.net) tests and analyze results for pass/fail within [Robot Framework](http://www.robotframework.org))

  * eyeBeam/X-Lite resource file (with high level user keywords to perform [eyeBeam/X-Lite](http://www.counterpath.com/x-lite.html) softphone automation, via [AutoItLibrary](http://code.google.com/p/robotframework-autoitlibrary/) for [Robot Framework](http://www.robotframework.org))

  * pcapdiffLibrary ([Robot Framework](http://www.robotframework.org) library interface to [pcapdiff](http://www.eff.org/testyourisp/pcapdiff) tool from [EFF](http://www.eff.org))

  * DetectDtmfFromFileLibrary (to detect DTMF from wave audio files. Based on Python library from http://sourceforge.net/projects/fbdtmfdetector )

  * ToneDetLibrary (to detect tones and DTMF from audio passing through [ToneDet](http://www.nch.com.au/action/misc.html) Windows-based tone detector)

  * Sox audio converter resource file (resource file to convert audio files via [Sox](http://sox.sourceforge.net) from within [Robot Framework](http://www.robotframework.org))

  * GoogleVoiceLibrary (based on [Google Voice Python library](http://code.google.com/p/pygooglevoice/).)

  * Some potential SMS libraries
    * using [Amazon Simple Notification Service (SNS)](http://aws.amazon.com/sns/)
    * using [Zeep Mobile](http://www.zeepmobile.com/developers/) API
    * using [Twilio API](http://www.twilio.com/api)

  * Some potential VoIP/SIP libraries
    * using [Twilio API](http://www.twilio.com/api)


# News / Updates #

  * 1/1/12 - no official releases, but some code and files are available in source code repository for you to try out. Sorry for lack of documentation or tests for libraries, but at least there's development code to work with. **NOTE:** consider the code offered here of Alpha quality, they're not production ready. With the eyebeam library being most complete (Beta). Not all the tools in the collection are code complete, I've not had time to come back to this after leaving my job in telecom industry.

# Contact #

For now, please direct all inquiries to the project admin. You could also post inquiries to [Robot Framework Users Google Group](http://groups.google.com/group/robotframework-users) as I am a member of that group and periodically check it. If there is enough inquiry activity, I may start a Google Group, etc. for it.