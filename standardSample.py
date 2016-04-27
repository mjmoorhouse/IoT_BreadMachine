#!/usr/bin/python
"""
standardSample.py

This program is designed to run with the SPI / ADC setup and - originally - monitor
power flow (formally current converted to voltage) but likely has other uses.
It is designed for use with a Raspberry PI and a MCP3008 ADC chip coupled to 
the SPI bus.

The chip specific communications are copied almost verbatim from this post:
http://www.raspberrypi-spy.co.uk/2013/10/analogue-sensors-on-the-raspberry-pi-using-an-mcp3008/
(with minor parameter tweaks).  The sensor is assumed to be on ADC input channel 0.

It samples ~2 cycles of 60Hz mains and then averages the results printing them to file
for further processing, the format is the same as \'fast sample\' format (in summary a 
direct dump of the raw values).
(SAMPLES_TO_TAKE = 250)

Without any parameters the program defaults to running for 1.5h and sampling every 2s.
(DEFAULT_RUN_TIME = 90 , DEFAULT_SAMPLE_TIME = 2)

Parameters:
If the program is run with a numeric parameter then this is used as the length of 
time in hours to run for.

If run with 2 parameters:
The first is assumed to be the length of time to run for in minutes 
The second is assumed to be the delay between samples; note that setting sample times shorter 
that time taken to actually take the sample is possible - and allowed - and then the 
program will sample continuosly at maximum rate.

Output File Format:
The file format is deliberately very simple to aid fast creation and reading.
The values are:
 Line 1: The start time of the complete data set in human readable format
 Line 2: The sampling rate per second (scaled if <1s of sampling)
 Line 3: The minute into the sampling, the index of the sample and the start & end times in seconds

e.g.:

 # Human Start Time:     Mon, 25 Apr 2016 15:51
 #Sample rate:    7426.47947573 / s
 #0      5       1461614331.241461614331.28
 0       388
 1       553
 2       412
 3       390

...etc...

Typical Output:
This is the typical CLI output from a 1 minute total sample time, sampling every 10s:
 $ ./standardSample.py 1 10
 Start Time: 1461614291.2	Mon-25-Apr-2016_15:58
 Run time is: 	60s with 10.0s pause between samples
 Predicted end time is:		Mon-25-Apr-2016_15:59
 Sampling 	1	 at: 1461614291.21 into file: waveform_1461614291.21.dat
  - Waiting: 9.954 s until next sample
 Sampling 	2	 at: 1461614301.21 into file: waveform_1461614301.21.dat
  - Waiting: 9.958 s until next sample
 Sampling 	3	 at: 1461614311.22 into file: waveform_1461614311.22.dat
  - Waiting: 9.958 s until next sample
 Sampling 	4	 at: 1461614321.23 into file: waveform_1461614321.23.dat
  - Waiting: 9.957 s until next sample
 Sampling 	5	 at: 1461614331.24 into file: waveform_1461614331.24.dat
  - Waiting: 9.958 s until next sample
 Sampling 	6	 at: 1461614341.26 into file: waveform_1461614341.26.dat
  - Waiting: 9.958 s until next sample
 End Time: 1461614351.27	M

Typical files and filesizes:
 $ ls -lthr Mon-25-Apr-2016_15\:58/*               
 -rw-r--r-- 1 pi pi 2.0K Apr 25 15:58 Mon-25-Apr-2016_15:58/waveform_1461614291.21.dat
 -rw-r--r-- 1 pi pi 2.0K Apr 25 15:58 Mon-25-Apr-2016_15:58/waveform_1461614301.21.dat
 -rw-r--r-- 1 pi pi 2.0K Apr 25 15:58 Mon-25-Apr-2016_15:58/waveform_1461614311.22.dat
 -rw-r--r-- 1 pi pi 2.0K Apr 25 15:58 Mon-25-Apr-2016_15:58/waveform_1461614321.23.dat
 -rw-r--r-- 1 pi pi 2.0K Apr 25 15:58 Mon-25-Apr-2016_15:58/waveform_1461614331.24.dat
 -rw-r--r-- 1 pi pi 2.0K Apr 25 15:59 Mon-25-Apr-2016_15:58/waveform_1461614341.26.dat

"""
#Mixture of OO and classical functional import statements:
import os
from sys import argv
import time
import datetime
import spidev

#Two defaults the CLI parameters can adapt:
DEFAULT_RUN_TIME = 90 	#Time in minutes
DEFAULT_SAMPLE_TIME = 2 #Time in seconds
SAMPLES_TO_TAKE = 250	#~ 2 cycles at 60Hz and the ADC speed

#Set defaults that we might change using CLI paramters:
samplePauseTime = DEFAULT_SAMPLE_TIME	# How long to pause between samples
runTime = 60 *  DEFAULT_RUN_TIME	# When to run until

#The time when we we stop: (last term in minutes)
if len(argv) >= 2:
	runTime = 60 * float(argv[1])
if len(argv) >= 3:
	samplePauseTime = float(argv[2])

#Set our start & end times:
startTime = time.time()
endTime = startTime + runTime

#Print these out:
print ("Start Time: " + str(time.time()) + "\t" + 
	str(time.strftime("%a-%d-%b-%Y_%H:%M",time.localtime(time.time()))))
print ("Run time is: \t" + str (int(runTime)) + "s with " + str(samplePauseTime) 
	+ "s pause between samples")
print ("Predicted end time is:\t\t" + str(time.strftime("%a-%d-%b-%Y_%H:%M",
	time.localtime(endTime))))

# Determine the new directory to work in:
runBaseName = time.strftime("%a-%d-%b-%Y_%H:%M",time.localtime(startTime))

#Create the directory and switch into it:
os.makedirs(str(runBaseName))
os.chdir(str(runBaseName))

# Open SPI bus
spi = spidev.SpiDev()
spi.open(0,0)
spi.max_speed_hz=(4000000)	#Don't bother increasing this: the MCP3008 won't go faster at 3.3V Vcc

#Initialisation phase complete!


#The data-get / sampling function, copied verbatim from: 
#http://www.raspberrypi-spy.co.uk/2013/10/analogue-sensors-on-the-raspberry-pi-using-an-mcp3008/
def ReadChannel(channel):
  adc = spi.xfer2([1,(8+channel)<<4,0])
  data = ((adc[1]&3) << 8) + adc[2]
  return data

"""
This collects, then dumps into a new time-stamped file the raw values
obtained along with some basic time stamp information in a header section.
"""
#A simple loop / sample number counter:
sampleIndex = 0;

#The main loop:

while endTime >= time.time():
	sampleIndex = sampleIndex +1 #Increment the loop counter
	sampleStartTime=time.time()
	#Build the output filename:
	fileName= "waveform_" + str(sampleStartTime)+".dat"
	#Print out to console:
	print ("Sampling \t"+ str(sampleIndex) + "\t at: " + 
	str(sampleStartTime) + " into file: " + fileName)

	#Open it:
	target =open (fileName, 'w')
	#Print Header information:
	target.write ("# Human Start Time:\t" + \
		time.strftime("%a, %d %b %Y %H:%S",time.localtime(sampleStartTime))+"\n")

	Data = list ()
	#Main sample loop: fast as possible, direct to disk buffer:
	for i in range(0,SAMPLES_TO_TAKE):
		#Fast as we can: read off the DAC and stow in array
		Data.append(ReadChannel(0))
	    	
        #Note when we got all our data:
	sampleEndTime=time.time()
	#How long & fast it took:
	sampleInterval=float(sampleEndTime - sampleStartTime)
	sampleRate = (len(Data)+1) / sampleInterval  
#	print ("Sample rate: " + str(sampleInterval) + "  " + str(sampleRate) + "\n")
	#The minute into the sampling: a convenience for quick scanning manually:
	sampleMinute = int((sampleStartTime - startTime) / 60)
	#Print the sample rate:

	target.write ("#Sample rate: \t " + str(sampleRate) + " / s" + "\n")
    	#Time Stamp the head of the file:
	target.write ("#" + str(sampleMinute) + "\t" + 
		str(sampleIndex) + "\t" + str(sampleStartTime) +
		str(sampleEndTime) + "\n")
	
	#Write out the collected data:
	for  i in range (0, len(Data)):
		          # Read the data off the ADC straight into the write buffer:
		target.write(str(i) + "\t" + str(Data[i]) + "\n")
	target.close()
#End main sample section
#How long to wait to our next sample?
	waitTime = (samplePauseTime + sampleStartTime) - time.time()
	#If we should have already done it: don't wait - run at full speed!
	if waitTime > 0:
		print (" - Waiting: " + str(round(waitTime,3)) + " s until next sample")
		time.sleep (waitTime)
print ("End Time: " + str(time.time()) + "\t" + 
	str(time.strftime("%a, %d %b %Y %H:%S",time.localtime(time.time()))))
print ("All Done!")
