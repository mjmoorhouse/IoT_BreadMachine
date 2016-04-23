# IoT_BreadMachine
An 'Internet of Things' Bread Machine project / Mains Power Flow monitor project

## Introduction
This project demonstrates the use of an Analogue to Digitial Convertor chip (MCP3008), a Raspberry PI (B+) to non-invasively monitor power flow in a mains cable via the means of 'Current Clamp' _(actually and clip-round-the-cable-transformer that looks like a 'clamp')_ during different phases of the bread machine's cycle (somecombination of: _kneed, rise, bake, keep warm_).  The raw waveform is sampled using Python code and the SPI interface to communicate with the MCP3008 ship and then either write the raw values to the filesystem or summarise features of sample taken.  Further exploratory analysis is done in 'R' currently with a non-specific plan to formalise the insights into an online / realtime Python classification program ultimately.

## Technical Details
See the original presentation for details of the hardware setup - including pictures but briefly: the ADC is lashed to the R-Pi using an IDC header cable and breadboard.  The ADC is run from the 3.3V power supply and samples the voltage across a 'laod' resistor connected to the 'Clamp'.  The SPI (Serial Perhipheral Interface) is used to send setup intstructions to and receive data from the ADC using a series of low-level bit manipulations in Python.  The result being captured in a classical python list of numbers 0-1023 at a rate of upto 7000 samples a second (~130 samples over a 60Hz waveform).  

The original code used the python 'scheduler' module - to do both 'fast' (raw dump of waveform) or 'slow' sampling (average, outlier exclusion, timestamps).  Where possible the output data formats obeyed the best principals of [_tidy data_](https://www.jstatsoft.org/article/view/v059i10) and are designed for easy automatic processing.

## Initial Presentation 
The initial presentation of the material was at the Toronto, Canada, Python Meetup group in January 2016 see [here](http://www.meetup.com/Python-Toronto/events/228102106/).
