# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models
from django.conf import settings
from django.contrib.auth.models import User
from django.http import HttpResponseRedirect
from django.shortcuts import render, redirect, render_to_response
from django.urls import reverse
from django.utils.encoding import python_2_unicode_compatible
from shutil import copyfile
#from .chocolate import *
import datetime
import shutil
import os


#    Final Variables --------------------------------------------------------------------------------
MAX_CHAR_FIELD = 100
MAX_LID_FIELD = 255
MAX_TEXT_FIELD = 1000

PDS4_LABEL_TEMPLATE_DIRECTORY = os.path.join(settings.TEMPLATE_DIR, 'pds4_labels')







# Create your models here.

"""
10.21  Investigation_Area

Root Class:Product_Components
Role:Concrete

Class Description:The Investigation_Area class provides information about an investigation (mission, observing campaign or other coordinated, large-scale data collection effort).

Steward:pds
Namespace Id:pds
Version Id:1.1.0.0
  	Entity 	Card 	Value/Class 	Ind

Hierarchy	Product_Components	 	 	 
 	        . Investigation_Area	 	 	 
Subclass	none	 	 	 
Attribute	name	1	 	 
 	        type	1	Individual Investigation	 
 	 	 	        Mission	 
         	 	 	Observing Campaign	 
 	         	 	Other Investigation	 
Inherited Attribute	none	 	 	 
Association	        internal_reference	1..*	Internal_Reference	 
Inherited Association	none	 	 	 

Referenced from	Context_Area	 	 	 
        	Observation_Area	 	 	 
"""
class Investigation(models.Model):
    INVESTIGATION_TYPES = [
        ('individual','individual'),
        ('mission','mission'),
        ('observing_campaign','observingcampaign'),
        ('other_investigation','other_investigation'),
    ]
    name = models.CharField(max_length=MAX_CHAR_FIELD)
    type_of = models.CharField(max_length=MAX_CHAR_FIELD, choices=INVESTIGATION_TYPES)
    version = models.PositiveIntegerField(default=0)
    starbase_label = models.CharField(max_length=MAX_CHAR_FIELD)








"""
14.2  Facility

Root Class:Tagged_NonDigital_Object
Role:Concrete

Class Description:The Facility class provides a name and address for a terrestrial observatory or laboratory.

Steward:pds
Namespace Id:pds
Version Id:1.0.0.0
  	Entity 	Card 	Value/Class 	Ind
Hierarchy	Tagged_NonDigital_Object	 	 	 
         	. TNDO_Context	 	 	 
 	        . . Facility	 	 	 
Subclass	none	 	 	 
Attribute	address	        0..1	 	 
 	        country	        0..1	 	 
 	        description	0..1	 	 
 	        name	        0..1	 	 
 	        type	        1	Laboratory	 
 	 	         	        Observatory	 

Inherited Attribute	none	 	 	 
Association	        data_object	1	Physical_Object	 
Inherited Association	none	 	 	 

Referenced from	Product_Context	 	 	 
"""
@python_2_unicode_compatible
class Facility(models.Model):
    FACILITY_TYPES = [
        ('Laboratory','Laboratory'),
        ('Observatory','Observatory'),
    ]

    address = models.CharField(max_length=MAX_CHAR_FIELD)
    country = models.CharField(max_length=MAX_CHAR_FIELD)
    description = models.CharField(max_length=MAX_TEXT_FIELD) # Use a widget in forms if need be 
    investigation = models.ManyToManyField(Investigation)
    name = models.CharField(max_length=MAX_CHAR_FIELD)
    logical_identifier = models.CharField(max_length=MAX_CHAR_FIELD)
    type_of = models.CharField(max_length=MAX_CHAR_FIELD, choices=FACILITY_TYPES) 

    # Accessors
    def name_lid_case(self):
        # Convert name to lower case
        name_edit = self.name.lower()
        # Convert spaces to underscores
        name_edit = replace_all(name_edit, ' ', '_')

    # Meta
    def __str__(self):
        return self.name








"""
10.25  Mission_Area

Root Class:Product_Components
Role:Concrete

Class Description:The mission area allows the insertion of mission specific metadata.

Steward:pds
Namespace Id:pds
Version Id:1.0.0.0
  	Entity 	Card 	Value/Class 	Ind

Hierarchy	Product_Components	 	 	 
        	. Mission_Area	 	 	 
Subclass        	none	 	 	 
Attribute	        none	 	 	 
Inherited Attribute	none	 	 	 
Association	        none	 	 	 
Inherited Association	none	 	 	 
Referenced from	Context_Area	 	 	 
         	Observation_Area	 	 	 
"""
@python_2_unicode_compatible
class Mission(models.Model):
    investigation = models.ManyToManyField(Investigation)
    name = models.CharField(max_length=MAX_CHAR_FIELD)

    # Accessors
    def name_lid_case(self):
        # Convert name to lower case
        name_edit = self.name.lower()
        # Convert spaces to underscores
        name_edit = replace_all(name_edit, ' ', '_')
        

    # Meta
    def __str__(self):
        return self.name








"""
14.4  Instrument_Host

Root Class:Tagged_NonDigital_Object
Role:Concrete

Class Description:The Instrument Host class provides a description of the physical object upon which an instrument is mounted.

Steward:pds
Namespace Id:pds
Version Id:1.3.0.0
  	Entity 	Card 	Value/Class 	Ind
Hierarchy	Tagged_NonDigital_Object	 	 	 
        	. TNDO_Context	 	 	 
        	. . Instrument_Host	 	 	 
Subclass	none	 	 	 

Attribute	description	                        1	 	 
        	instrument_host_version_id *Deprecated*	0..1	 	 
        	naif_host_id	                        0..1	 	 
        	name	                                0..1	 	 
        	serial_number	                        0..1	 	 
        	type	                                1	Earth Based	 
 	 	 	                                        Earth-based	 
 	 	 	                                        Lander	 
 	 	 	                                        Rover	 
 	 	 	                                        Spacecraft	 
        	version_id *Deprecated*	                0..1	 	 

Inherited Attribute	none	 	 	 
Association     	data_object	1	Physical_Object	 
Inherited Association	none	 	 	 

Referenced from	Product_Context	 	 	 
"""
@python_2_unicode_compatible
class InstrumentHost(models.Model):
    INSTRUMENT_HOST_TYPES = [
        ('Earth Based','Earth Based'),
        ('Lander', 'Lander'),
        ('Rover', 'Rover'),
        ('Spacecraft','Spacecraft'),
    ]
    description = models.CharField(max_length=MAX_TEXT_FIELD)
    mission = models.ForeignKey(Mission, on_delete=models.CASCADE)
    name = models.CharField(max_length=MAX_CHAR_FIELD)
    naif_host_id = models.CharField(max_length=MAX_CHAR_FIELD)
    serial_number = models.CharField(max_length=MAX_CHAR_FIELD)
    type_of = models.CharField(max_length=MAX_CHAR_FIELD, choices=INSTRUMENT_HOST_TYPES)

    # Meta
    def __str__(self):
        return self.name








"""
14.3  Instrument

Root Class:Tagged_NonDigital_Object
Role:Concrete

Class Description:The Instrument class provides a description of a physical object that collects data.

Steward:pds
Namespace Id:pds
Version Id:1.3.0.0
  	Entity 	Card 	Value/Class 	Ind
Hierarchy	Tagged_NonDigital_Object	 	 	 
        	. TNDO_Context	 	 	 
 	        . . Instrument	 	 	 
Subclass	none	 	 	 

Attribute	description	        1	 	 
        	model_id	        0..1	 	 
                naif_instrument_id	0..1	 	 
        	name	                0..1	 	 
 	        serial_number	        0..1	 	 
 	        subtype	                0..*	 	 
 	        type	                1..*	Accelerometer	 
                        	 	 	Alpha Particle Detector	 
                        	 	 	Alpha Particle X-Ray Spectrometer	 
                        	 	 	Altimeter	 
                        	 	 	Anemometer	 
                        	 	 	Atmospheric Sciences	 
                        	 	 	Atomic Force Microscope	 
                        	 	 	Barometer	 
                        	 	 	Biology Experiments	 
                        	 	 	Bolometer	 
                        	 	 	Camera	 
                        	 	 	Cosmic Ray Detector	 
                        	 	 	Drilling Tool	 
                        	 	 	Dust	 
                        	 	 	Dust Detector	 
                        	 	 	Electrical Probe	 
                        	 	 	Energetic Particle Detector	 
                        	 	 	Gamma Ray Detector	 
                        	 	 	Gas Analyzer	 
                        	 	 	Gravimeter	 
                        	 	 	Grinding Tool	 
                        	 	 	Hygrometer	 
                        	 	 	Imager	 
                        	 	 	Imaging Spectrometer	 
                        	 	 	Inertial Measurement Unit	 
                        	 	 	Infrared Spectrometer	 
                        	 	 	Interferometer	 
                        	 	 	Laser Induced Breakdown Spectrometer	 
                        	 	 	Magnetometer	 
                        	 	 	Mass Spectrometer	 
                        	 	 	Microscope	 
                        	 	 	Microwave Spectrometer	 
                        	 	 	Moessbauer Spectrometer	 
                        	 	 	Naked Eye	 
                        	 	 	Neutral Particle Detector	 
                        	 	 	Neutron Detector	 
                        	 	 	Particle Detector	 
                        	 	 	Photometer	 
                        	 	 	Plasma Analyzer	 
                        	 	 	Plasma Detector	 
                        	 	 	Plasma Wave Spectrometer	 
                        	 	 	Polarimeter	 
                        	 	 	Radar	 
                        	 	 	Radio Science	 
                        	 	 	Radio Spectrometer	 
                        	 	 	Radio Telescope	 
                        	 	 	Radio-Radar	 
                        	 	 	Radiometer	 
                        	 	 	Reflectometer	 
                        	 	 	Regolith Properties	 
                        	 	 	Robotic Arm	 
                        	 	 	Seismometer	 
                        	 	 	Small Bodies Sciences	 
                        	 	 	Spectrograph	 
                        	 	 	Spectrograph Imager	 
                        	 	 	Spectrometer	 
                        	 	 	Thermal Imager	 
                        	 	 	Thermal Probe	 
                        	 	 	Thermometer	 
                        	 	 	Ultraviolet Spectrometer	 
                        	 	 	Weather Station	 
                        	 	 	Wet Chemistry Laboratory	 
                        	 	 	X-ray Detector	 
                        	 	 	X-ray Diffraction Spectrometer	 
                        	 	 	X-ray Fluorescence Spectrometer	 
Inherited Attribute	none	 	 	 
Association      	data_object	1	Physical_Object	 
Inherited Association	none	 	 	 

Referenced from	Product_Context	 	 	 
"""
class Instrument(models.Model):
    INSTRUMENT_TYPES = [
        ('Accelerometer','Accelerometer'),
        ('Alpha Particle Detector','Alpha Particle Detector'),
        ('Alpha Particle X-Ray Spectrometer','Alpha Particle X-Ray Spectrometer'),
        ('Altimeter','Altimeter'),
        ('Anemometer','Anemometer'),
        ('Atmospheric Sciences','Atmospheric Sciences'),
        ('Atomic Force Microscope','Atomic Force Microscope'),
        ('Barometer','Barometer'),
        ('Biology Experiments','Biology Experiments'),
        ('Bolometer','Bolometer'),
        ('Camera','Camera'),
        ('Cosmic Ray Detector','Cosmic Ray Detector'),
        ('Drilling Tool','Drilling Tool'),
        ('Dust','Dust'),
        ('Dust Detector','Dust Detector'),
        ('Electrical Probe','Electrical Probe'),
        ('Energetic Particle Detector','Energetic Particle Detector'),
        ('Gamma Ray Detector','Gamma Ray Detector'),
        ('Gas Analyzer','Gas Analyzer'),
        ('Gravimeter','Gravimeter'),
        ('Grinding Tool','Grinding Tool'),
        ('Hygrometer','Hygrometer'),
        ('Imager','Imager'),
        ('Imaging Spectrometer','Imaging Spectrometer'),
        ('Inertial Measurement Unit','Inertial Measurement Unit'),
        ('Infrared Spectrometer','Infrared Spectrometer'),
        ('Interferometer','Interferometer'),
        ('Laser Induced Breakdown Spectrometer','Laser Induced Breakdown Spectrometer'),
        ('Magnetometer','Magnetometer'),
        ('Mass Spectrometer','Mass Spectrometer'),
        ('Microscope','Microscope'),
        ('Microwave Spectrometer','Microwave Spectrometer'),
        ('Moessbauer Spectrometer','Moessbauer Spectrometer'),
        ('Naked Eye','Naked Eye'),
        ('Neutral Particle Detector','Neutral Particle Detector'),
        ('Neutron Detector','Neutron Detector'),
        ('Particle Detector','Particle Detector'),
        ('Photometer','Photometer'),
        ('Plasma Analyzer','Plasma Analyzer'),
        ('Plasma Detector','Plasma Detector'),
        ('Plasma Wave Spectrometer','Plasma Wave Spectrometer'),
        ('Polarimeter','Polarimeter'),
        ('Radar','Radar'),
        ('Radio Science','Radio Science'),
        ('Radio Spectrometer','Radio Spectrometer'),
        ('Radio Telescope','Radio Telescope'),
        ('Radio-Radar','Radio-Radar'),
        ('Radiometer','Radiometer'),
        ('Reflectometer','Reflectometer'),
        ('Regolith Properties','Regolith Properties'),
        ('Robotic Arm','Robotic Arm'),
        ('Seismometer','Seismometer'),
        ('Small Bodies Sciences','Small Bodies Sciences'),
        ('Spectrograph','Spectrograph'),
        ('Spectrograph Imager','Spectrograph Imager'),
        ('Spectrometer','Spectrometer'),
        ('Thermal Imager','Thermal Imager'),
        ('Thermal Probe','Thermal Probe'),
        ('Thermometer','Thermometer'),
        ('Ultraviolet Spectrometer','Ultraviolet Spectrometer'),
        ('Weather Station','Weather Station'),
        ('Wet Chemistry Laboratory','Wet Chemistry Laboratory'),
        ('X-ray Detector','X-ray Detector'),
        ('X-ray Diffraction Spectrometer','X-ray Diffraction Spectrometer'),
        ('X-ray Fluorescence Spectrometer','X-ray Fluorescence Spectrometer'),
    ]
    description = models.CharField(max_length=MAX_TEXT_FIELD)
    facility = models.ForeignKey(Facility, on_delete=models.CASCADE)  # This might be incorrect.
    instrument_host = models.ForeignKey(InstrumentHost)
    model_id = models.CharField(max_length=MAX_CHAR_FIELD)
    naif_instrument_id = models.CharField(max_length=MAX_CHAR_FIELD)
    name = models.CharField(max_length=MAX_CHAR_FIELD)
    serial_number = models.CharField(max_length=MAX_CHAR_FIELD)
    subtype = models.CharField(max_length=MAX_CHAR_FIELD)
    type_of = models.CharField(max_length=MAX_CHAR_FIELD, choices=INSTRUMENT_TYPES)

    # Meta
    def __str__(self):
        return self.name








"""
14.8  Target

Root Class:Tagged_NonDigital_Object
Role:Concrete
Class Description:The Target class provides a description of a physical object that is the object of data collection.
Steward:pds
Namespace Id:pds
Version Id:1.3.0.0
  	Entity 	Card 	Value/Class 	Ind
Hierarchy	Tagged_NonDigital_Object	 	 	 
 	. TNDO_Context	 	 	 
 	. . Target	 	 	 
Subclass	none	 	 	
Attribute	description	1	 	 
 	name	0..1	 	 
 	type	0..*	Asteroid	 
 	 	 	Calibration	 
 	 	 	Calibration Field	 
 	 	 	Calibrator	 
 	 	 	Comet	 
 	 	 	Dust	 
 	 	 	Dwarf Planet	 
 	 	 	Equipment	 
 	 	 	Exoplanet System	 
 	 	 	Galaxy	 
 	 	 	Globular Cluster	 
 	 	 	Lunar Sample	 
 	 	 	Meteorite	 
 	 	 	Meteoroid	 
 	 	 	Meteoroid Stream	 
 	 	 	Nebula	 
 	 	 	Open Cluster	 
 	 	 	Planet	 
 	 	 	Planetary Nebula	 
 	 	 	Planetary System	 
 	 	 	Plasma Cloud	 
 	 	 	Plasma Stream	 
 	 	 	Ring	 
 	 	 	Satellite	 
 	 	 	Star	 
 	 	 	Star Cluster	 
 	 	 	Sun	 
 	 	 	Synthetic Sample	 
 	 	 	Terrestrial Sample	 
 	 	 	Trans-Neptunian Object	 
Inherited Attribute	none	 	 	 
Association	data_object	1	Physical_Object	 
Inherited Association	none	 	 	 
Referenced from	Product_Context	 	 	 
"""
@python_2_unicode_compatible
class Target(models.Model):
    TARGET_TYPES = [
        ('Asteroid','Asteroid'),
        ('Calibration','Calibration'),
        ('Calibration Field','Calibration Field'),
        ('Calibrator','Calibrator'),
        ('Comet','Comet'),
        ('Dust','Dust'),
        ('Dwarf Planet','Dwarf Planet'),
        ('Equipment','Equipment'),
        ('Exoplanet System','Exoplanet System'),
        ('Galaxy','Galaxy'),
        ('Globular Cluster','Globular Cluster'),
        ('Lunar Sample','Lunar Sample'),
        ('Meteorite','Meteorite'),
        ('Meteoroid','Meteoroid'),
        ('Meteoroid Stream','Meteoroid Stream'),
        ('Nebula','Nebula'),
        ('Open Cluster','Open Cluster'),
        ('Planet','Planet'),
        ('Planetary Nebula','Planetary Nebula'),
        ('Planetary System','Planetary System'),
        ('Plasma Cloud','Plasma Cloud'),
        ('Plasma Stream','Plasma Stream'),
        ('Ring','Ring'),
        ('Satellite','Satellite'),
        ('Star','Star'),
        ('Star Cluster','Star Cluster'),
        ('Sun','Sun'),
        ('Synthetic Sample','Synthetic Sample'),
        ('Target Analog', 'Target Analog'),
        ('Terrestrial Sample','Terrestrial Sample'),
        ('Trans-Neptunian Object','Trans-Neptunian Object'),
    ]
    description = models.CharField(max_length=MAX_CHAR_FIELD)
    facility = models.ForeignKey(Facility, on_delete=models.CASCADE)
    mission = models.ForeignKey(Mission, on_delete=models.CASCADE)
    name = models.CharField(max_length=MAX_CHAR_FIELD)
    type_of = models.CharField(max_length=MAX_CHAR_FIELD, choices=TARGET_TYPES)

    # Meta
    def __str__(self):
        return self.name







