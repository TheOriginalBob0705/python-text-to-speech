SAM
===
Software Automatic Mouth - Tiny Speech Synthesizer 

What is SAM?
============
SAM (Software Automatic Mouth) is a Text-To-Speech (TTS) program originally written in Assembly for the Commodore 64, 
published in the year 1982 by Don't Ask Software (now SoftVoice, Inc.). It includes a Text-To-Phoneme converter called 
reciter and a Phoneme-To-Speech routine for the final output.

An online version and executables for Windows can be found on the web site: http://simulationcorner.net/index.php?page=sam

Adaption To Python
=============
This program was originally converted into C by GitHub user s-macke. Now I am attempting to convert it to Python.

Reciter
-------
It changes the english text to phonemes by a ruleset shown in the wiki.

The rule
	" ANT(I)",	"AY",
means that if he find an "I" with previous letters " ANT", exchange the I by the phoneme "AY".

There are some special signs in these rules like
	#
	&
	@
	^
	+
	:
	%
which can mean e.g. that there must be a vocal or a consonant or something else.

License
=======
The software is a reverse-engineered version of a commercial software published more than 30 years ago.
The current copyright holder is SoftVoice, Inc. (www.text2speech.com)

Any attempt to contact the company failed. The website was last updated in the year 2009.
The status of the original software can therefore best described as Abandonware 
(http://en.wikipedia.org/wiki/Abandonware)

As long this is the case I cannot put my code under any specific open source software license
Use it at your own risk.

Contact
=======
If you discovered some new knowledge about the original Assembly code please mail Sebastian:
Sebastian Macke
Email: sebastian@macke.de