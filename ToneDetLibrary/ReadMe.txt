TODO - create this library, or at least start template for it.

ToneDet.exe is a Windows GUI app that reads from config INI file.

Original toolset used VBScripts to set, check, and clear custom Windows registry flags that indicated whether particular tones were detected. For example 2200 Hz, DTMF. DTMF was detected as a pair of dual tone frequencies, so both of the appropriate tone frequency pairs but be flagged to indicate detection of corresponding DTMF digit. See

http://en.wikipedia.org/wiki/Dual-tone_multi-frequency_signaling

for reference.

The ToneDet program would be configured to execute the VBScripts that set detection flag in registry when detecting specified tones. We would preconfigure ToneDet to detect specific tones (all the DTMF tone frequencies, plus any needed custom ones like modem tone, dial tone, etc.).

Any automated or programmatic configuration of ToneDet would be via desktop win32 GUI automation via say the AutoItLibrary with RobotFramework, encapsulated here in this library.

The other VBScripts that check or clear flags are separately called.

This library will wrap all the ToneDet GUI configuration and VBScript execution into a single library.

This library should be implemented as a Python library unless it could easily be done as a resource file, which might be possible using command line tools to set, check, clear registry flags.

NOTE: Windows registry is used because ToneDet may detect tones multiple times resulting in race condition on writes, which would prevent use of INI/config files. Alternative is to use a database, and Windows registry is easier config to deploy than a database.