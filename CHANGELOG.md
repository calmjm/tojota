# Changelog

## [0.0.4] - 2020-11-12

### Added

- Function to get driving statistics
- Example script to print daily/weekly/yearly driving statistics, statistics.py

## [0.0.3] - 2020-11-09

### Fixed

- Fixed https://github.com/calmjm/tojota/issues/13, exception when latest address is not available

## [0.0.2] - 2020-10-21

### Added

- Get odometer and fuel level information
- Get remote control / HVAC status
- Report if data is new or cached
- Possibility to save data to InfluxDB

### Fixed

- Handle missing address fields in trip data
- Make cache file names Windows compatible

## [0.0.1] - 2020-05-01

### Added

- Do Toyota SSO login
- Get trips
- Get trip detailed information
- Get vehicle location
