# Changelog

## [0.0.7] - 2022-03-22

### Fixed

- Getting odometer information started to require headers X-TME-APP-VERSION and UUID and different authentication.
- Example app crashed when getting information failed.

### Known issues

- Getting odometer information still fails to "Token provided in the header is invalid". Requires more reverse engineering.

## [0.0.6] - 2021-10-14

### Fixed

- Added locale and brand parameters to statistics query to make it work again

## [0.0.5] - 2021-01-31

### Added

- Print out HV range
- Print out heating information when preheating is on
- More statistics to be print out

### Fixed

- Remote control API started to require (dummy) locale header
- Print out statistics missing EV data
- Statistics works at the beginning of the year, https://github.com/calmjm/tojota/issues/18
- Enforced UTF-8 when handling cache files, https://github.com/calmjm/tojota/issues/17
- Don't crash on missing parking info, https://github.com/calmjm/tojota/issues/16

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
