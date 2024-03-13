# Library for handling Toyota vehicle API

Unofficial python functions for handling data from Toyota Connected services APIs. https://www.toyota-europe.com/myt,
https://play.google.com/store/apps/details?id=com.toyota.oneapp.eu

# Installation

- Have Python 3.6+
- Create virtual environment
- Install requirements `pip install -r requirements.txt`

# Usage

- Configure your MyT user account, password and vehicle VIN into `configs/myt.json`
- If your vehicle doesn't support remote control functions, set "use_remote_control": false in the config file
- If you would like to save data to InfluxDB, install InfluxDB ( https://www.influxdata.com/ ) and create database
  'tojota' and set "use_influxdb": true in the config file (support only for old unsecure no authentication version)
- Run `python tojota.py` to fetch, save and print data
- Data is saved to cache directory for further usage

