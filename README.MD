# Mining Data Sets

## Purpose
The following repository gathers source code for scrubbing, aggregating, transforming, and visualizing real world data in support of Project 70's goals.
To prevent a network bottleneck for those wishing to clone this repository, the database associated with this code is not included in this repository; it contains only the source code used to generate a database.


## Flight Tracks
The code under the directory `adsbexchange` was used to aggregate 50 million time-stamped waypoints and vehicle-specific features (~ 16 GB) between March 5 and March 7, 2022.
The data was recieved by many ADS-B recievers across the consecutive US and hosted at [adsbexchange.com](https://globe.adsbexchange.com).
A few more modernized airports have started using ADS-B for coordinating ground crew vehicles; these waypoints are also included in the data set.

In addition to positional data, the waypoints also contain vehicle-specific identifying labels, serving a handful of possible use cases for ML-based kinematic classification.

## Current & Future Work
The issues that arose are highly specific and could be tackled by multiple team members without any background knowledge of the entire code base. They are summarized as follows.

* Multiple server requests are necessary to gather all the information each database row. A function in Python or SQLite should be written to aggregate overlapping waypoints and fix timing problems where multiple server requests were used.

* Due to unavoidable shutdowns for code updates, there exist some gaps in the data, and we would benefit from having a regression function for generating unseen waypoints on these.

* Remove “damaged” or erroneous data.


# Data Attributes

Each column of the database denote the following:

* messages: the total number of Mode S messages processed since readsb started.
* aircraft: an array of JSON objects, one per known aircraft. Each aircraft has the following keys. Keys will be omitted if data is not available.
* hex: the 24-bit ICAO identifier of the aircraft, as 6 hex digits. The identifier may start with ‘~’, this means that the address is a non-ICAO address (e.g. from TIS-B).
* type: type of underlying messages / best source of current data for this position / aircraft: (the following list is in order of which data is preferentially used)
* adsb_icao: messages from a Mode S or ADS-B transponder, using a 24-bit ICAO address
* adsb_icao_nt: messages from an ADS-B equipped “non-transponder” emitter e.g. a ground vehicle, using a 24-bit ICAO address
* adsr_icao: rebroadcast of ADS-B messages originally sent via another data link e.g. UAT, using a 24-bit ICAO address
* tisb_icao: traffic information about a non-ADS-B target identified by a 24-bit ICAO address, e.g. a Mode S target tracked by secondary radar
* adsc: ADS-C (received by monitoring satellite downlinks)
* mlat: MLAT, position calculated arrival time differences using multiple receivers, outliers and varying accuracy is expected.
* other: miscellaneous data received via Basestation / SBS format, quality / source is unknown.
* mode_s: ModeS data from the planes transponder (no position transmitted)
* adsb_other: messages from an ADS-B transponder using a non-ICAO address, e.g. anonymized address
* adsr_other: rebroadcast of ADS-B messages originally sent via another data link e.g. UAT, using a non-ICAO address
* tisb_other: traffic information about a non-ADS-B target using a non-ICAO address
* tisb_trackfile: traffic information about a non-ADS-B target using a track/file identifier, typically from primary or Mode A/C radar
* flight: callsign, the flight name or aircraft registration as 8 chars (2.2.8.2.6)
* r: aircraft registration pulled from database
* t: aircraft type pulled from database
* dbFlags: bitfield for certain database flags use a bitwise AND (&). Check the documentation for your programming language.
* military = dbFlags & 1;
* interesting = dbFlags & 2;
* PIA = dbFlags & 4;
* LADD = dbFlags & 8;
* alt_baro: the aircraft barometric altitude in feet
* alt_geom: geometric (GNSS / INS) altitude in feet referenced to the WGS84 ellipsoid
* gs: ground speed in knots
* ias: indicated air speed in knots
* tas: true air speed in knots
* mach: Mach number
* track: true track over ground in degrees (0-359)
* track_rate: Rate of change of track, degrees/second
* roll: Roll, degrees, negative is left roll
* mag_heading: Heading, degrees clockwise from magnetic north
* true_heading: Heading, degrees clockwise from true north (usually only transmitted on ground, in the air usually derived from the magnetic heading using magnetic model WMM2020)
* baro_rate: Rate of change of barometric altitude, feet/minute
* geom_rate: Rate of change of geometric (GNSS / INS) altitude, feet/minute
* squawk: Mode A code (Squawk), encoded as 4 octal digits
* rr_lat, rr_lon: If no ADS-B or MLAT position available, a rough estimated position for the aircraft based on the receiver’s coordinates.
* emergency: ADS-B emergency/priority status, a superset of the 7×00 squawks (2.2.3.2.7.8.1.1)
* category: emitter category to identify particular aircraft or vehicle classes (values A0 – D7) (2.2.3.2.5.2)
* nav_qnh: altimeter setting (QFE or QNH/QNE), hPa
* nav_altitude_mcp: selected altitude from the Mode Control Panel / Flight Control Unit (MCP/FCU) or equivalent equipment
* nav_altitude_fms: selected altitude from the Flight Manaagement System (FMS) (2.2.3.2.7.1.3.3)
* nav_heading: selected heading (True or Magnetic is not defined in DO-260B, mostly Magnetic as that is the de facto standard) (2.2.3.2.7.1.3.7)
* nav_modes: set of engaged automation modes: ‘autopilot’, ‘vnav’, ‘althold’, ‘approach’, ‘lnav’, ‘tcas’
* lat, lon: the aircraft position in decimal degrees
* nic: Navigation Integrity Category (2.2.3.2.7.2.6)
* rc: Radius of Containment, meters; a measure of position integrity derived from NIC & supplementary bits. (2.2.3.2.7.2.6, Table 2-69)
* seen_pos: how long ago (in seconds before “now”) the position was last updated
* track: true track over ground in degrees (0-359)
* version: ADS-B Version Number 0, 1, 2 (3-7 are reserved) (2.2.3.2.7.5)
* nic_baro: Navigation Integrity Category for Barometric Altitude (2.2.5.1.35)
* nac_p: Navigation Accuracy for Position (2.2.5.1.35)
* nac_v: Navigation Accuracy for Velocity (2.2.5.1.19)
* sil: Source Integity Level (2.2.5.1.40)
* sil_type: interpretation of SIL: unknown, perhour, persample
* gva: Geometric Vertical Accuracy (2.2.3.2.7.2.8)
* sda: System Design Assurance (2.2.3.2.7.2.4.6)
* mlat: list of fields derived from MLAT data
* tisb: list of fields derived from TIS-B data
* messages: total number of Mode S messages received from this aircraft
* seen: how long ago (in seconds before “now”) a message was last received from this aircraft
* rssi: recent average RSSI (signal power), in dbFS; this will always be negative.
* alert: Flight status alert bit (2.2.3.2.3.2)
* spi: Flight status special position identification bit (2.2.3.2.3.2)
* wd, ws: wind direction, wind speed: calculated from ground track, true heading, true airspeed and ground speed
* oat, tat: outer air temperate, total air temperature: calculated from mach number and true airspeed (typically somewhat inaccurate at lower altitudes / mach numbers below 0.5)
