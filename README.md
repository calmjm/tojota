# Library for handling Toyota vehicle API

Unofficial python functions for handling data from Toyota Connected services APIs. https://www.toyota-europe.com/myt,
https://play.google.com/store/apps/details?id=app.mytoyota.toyota.com.mytoyota

# Installation

- Create virtual environment
- Install requirements `pip install -r requirements.txt`

# Usage

- Configure your MyT user account, password and vehicle VIN into `configs/myt.json`
- If your vehicle doesn't support remote control functions, set "use_remote_control": false in the config file
- If you would like to save data to InfluxDB, install InfluxDB ( https://www.influxdata.com/ ) and create database
  'tojota' and set "use_influxdb": true in the config file
- Run `python tojota.py` to fetch, save and print data
- Data is saved to cache directory for further usage

# Example run
```
$ python tojota.py
2020-10-21 22:10:44,132:__main__:INFO: Fetching trips...
2020-10-21 22:10:45,692:__main__:INFO: Get parking info...
Car is parked at Xxxxxkatu 16, 91800 Tyrnävä, Finland at 2020-10-21 16:30:15
2020-10-21 22:10:46,195:__main__:INFO: Get odometer info...
Odometer 3682 km, 10.0% fuel left
2020-10-21 22:10:46,580:__main__:INFO: Get remote control status...
Battery level 30%, EV range 0.0 km, Inside temperature 24, Charging status waitingForCharging, status reported at 2020-10-21 16:32:18
2020-10-21 16:04:40 Kangaskontiontie 27, 90240 Oulu -> 2020-10-21 16:30:15 Xxxxxkatu 16, 91800 Tyrnävä: 29.037 km, 68.1 km/h, 2.36 l/100 km, 0.68 l
2020-10-21 07:19:37 Xxxxxkatu 17, 91800 Tyrnävä -> 2020-10-21 07:45:21 Kangaskontiontie 27, 90240 Oulu: 28.19 km, 65.73 km/h, 0.00 l/100 km, 0.00 l
2020-10-20 16:03:58 Kangaskontiontie 27, 90240 Oulu -> 2020-10-20 16:28:14 Xxxxxkatu 16, 91800 Tyrnävä: 29.028 km, 71.77 km/h, 2.48 l/100 km, 0.72 l
2020-10-20 07:18:15 Xxxxxkatu 16, 91800 Tyrnävä -> 2020-10-20 07:41:46 Kangaskontiontie 27, 90240 Oulu: 28.193 km, 71.93 km/h, 0.00 l/100 km, 0.00 l
2020-10-19 16:45:29 Pauketie 4, 90410 Oulu -> 2020-10-19 17:08:13 Xxxxxkatu 16, 91800 Tyrnävä: 26.595 km, 70.19 km/h, 3.74 l/100 km, 0.99 l
2020-10-19 16:03:41 Kangaskontiontie 27, 90240 Oulu -> 2020-10-19 16:13:17 Pauketie 4, 90410 Oulu: 5.521 km, 34.51 km/h, 0.00 l/100 km, 0.00 l
2020-10-19 08:48:34 K Irkkotie 9, 91800 Tyrnävä -> 2020-10-19 09:12:00 Kangaskontiontie 27, 90240 Oulu: 28.521 km, 73.03 km/h, 0.00 l/100 km, 0.00 l
2020-10-19 08:06:19 Xxxxxkatu 16, 91800 Tyrnävä -> 2020-10-19 08:10:34 K Irkkotie 10, 91800 Tyrnävä: 1.488 km, 21.01 km/h, 0.00 l/100 km, 0.00 l
2020-10-16 17:02:41 Myllytie 1, 90450 Kempele -> 2020-10-16 17:20:55 Xxxxxkatu 16, 91800 Tyrnävä: 19.36 km, 63.71 km/h, 0.36 l/100 km, 0.07 l
2020-10-16 16:34:50 Myllytie 5, 90450 Kempele -> 2020-10-16 16:36:07 Myllytie 1, 90450 Kempele: 0.227 km, 10.61 km/h, 0.00 l/100 km, 0.00 l
2020-10-16 16:15:52 Kangaskontiontie 27, 90240 Oulu -> 2020-10-16 16:28:43 Myllytie 5, 90450 Kempele: 11.258 km, 52.57 km/h, 0.00 l/100 km, 0.00 l
2020-10-16 07:17:01 Xxxxxkatu 16, 91800 Tyrnävä -> 2020-10-16 07:41:49 Kangaskontiontie 27, 90240 Oulu: 28.189 km, 68.2 km/h, 1.59 l/100 km, 0.45 l
2020-10-15 16:06:18 Kangaskontiontie 27, 90240 Oulu -> 2020-10-15 16:30:59 Xxxxxkatu 16, 91800 Tyrnävä: 29.013 km, 70.52 km/h, 2.32 l/100 km, 0.67 l
2020-10-15 11:59:21 Nujulantie, 90410 Oulu -> 2020-10-15 12:06:01 Kangaskontiontie 27, 90240 Oulu: 3.626 km, 32.63 km/h, 0.00 l/100 km, 0.00 l
2020-10-15 11:18:32 Kangaskontiontie 27, 90240 Oulu -> 2020-10-15 11:25:22 Nujulantie, 90410 Oulu: 3.591 km, 31.53 km/h, 0.00 l/100 km, 0.00 l
2020-10-15 07:18:59 Xxxxxkatu 16, 91800 Tyrnävä -> 2020-10-15 07:43:23 Kangaskontiontie 27, 90240 Oulu: 28.193 km, 69.33 km/h, 0.00 l/100 km, 0.00 l
Total distance: 300.030 km, Fuel consumption: 3.59 l, 1.20 l/100 km
```

# Example data

## trips.json

```json
{
  "recentTrips": [
    {
      "tripId": "F769AA77-1D6C-41A1-B768-435A89BDD248",
      "startAddress": "Taivalkoski Teboil, 93400 Taivalkoski, Finland",
      "startTimeGmt": "2020-04-29T16:37:33Z",
      "endAddress": "Xxxxtie 19, 93999 Kuusamo, Finland",
      "endTimeGmt": "2020-04-29T17:06:37Z",
      "classificationType": 0
    },
    {
      "tripId": "DCC11F85-26A9-47D8-8AAC-BBB014DB57A3",
      "startAddress": "Kauppatie 9, 93400 Taivalkoski, Finland",
      "startTimeGmt": "2020-04-29T16:31:32Z",
      "endAddress": "Taivalkoski Teboil, 93400 Taivalkoski, Finland",
      "endTimeGmt": "2020-04-29T16:33:38Z",
      "classificationType": 0
    },
    {
      "tripId": "CDD0652C-80AB-4121-B252-E5257FDD3FC9",
      "startAddress": "Xxxxkuja 19, 91800 Tyrnävä, Finland",
      "startTimeGmt": "2020-04-29T14:07:04Z",
      "endAddress": "Kauppatie 9, 93400 Taivalkoski, Finland",
      "endTimeGmt": "2020-04-29T16:12:23Z",
      "classificationType": 0
    },
    {
      "tripId": "6D315842-25C3-4983-B597-EC9B038CD15D",
      "startAddress": "Haaransuontie 19, 90240 Oulu, Finland",
      "startTimeGmt": "2020-04-29T12:50:29Z",
      "endAddress": "Xxxxkuja 19, 91800 Tyrnävä, Finland",
      "endTimeGmt": "2020-04-29T13:19:52Z",
      "classificationType": 0
    },
    {
      "tripId": "58B8D8E9-3BD5-447F-BB27-FD08E2BF3FDC",
      "startAddress": "Xxxxkuja 19, 91800 Tyrnävä, Finland",
      "startTimeGmt": "2020-04-29T04:01:13Z",
      "endAddress": "Haaransuontie 19, 90240 Oulu, Finland",
      "endTimeGmt": "2020-04-29T04:31:52Z",
      "classificationType": 0
    },
    {
      "tripId": "71AE13A4-1161-44F6-9506-D42901D65DEB",
      "startAddress": "Myllytie 3, 90450 Kempele, Finland",
      "startTimeGmt": "2020-04-28T15:09:18Z",
      "endAddress": "Xxxkuja 19, 91800 Tyrnävä, Finland",
      "endTimeGmt": "2020-04-28T15:26:21Z",
      "classificationType": 0
    },
    {
      "tripId": "2494F83E-24E6-4FA5-844C-B70D0AF6ACD9",
      "startAddress": "Myllytie 1, 90450 Kempele, Finland",
      "startTimeGmt": "2020-04-28T14:45:03Z",
      "endAddress": "Myllytie 3, 90450 Kempele, Finland",
      "endTimeGmt": "2020-04-28T14:46:10Z",
      "classificationType": 0
    },
    {
      "tripId": "A86033F1-80CB-4D50-8821-2837EA178036",
      "startAddress": "Xxxxkuja 19, 91800 Tyrnävä, Finland",
      "startTimeGmt": "2020-04-28T14:16:53Z",
      "endAddress": "Myllytie 1, 90450 Kempele, Finland",
      "endTimeGmt": "2020-04-28T14:32:48Z",
      "classificationType": 0
    },
    {
      "tripId": "91F60F30-012A-4214-9C40-2FB2A72D9027",
      "startAddress": "Haaransuontie 19, 90240 Oulu, Finland",
      "startTimeGmt": "2020-04-28T13:07:07Z",
      "endAddress": "Xxxxkuja 19, 91800 Tyrnävä, Finland",
      "endTimeGmt": "2020-04-28T13:32:16Z",
      "classificationType": 0
    },
    {
      "tripId": "05ED3F3F-1A66-430C-B426-51B60AE683F5",
      "startAddress": "Xxxxkuja 19, 91800 Tyrnävä, Finland",
      "startTimeGmt": "2020-04-28T04:15:21Z",
      "endAddress": "Haaransuontie 19, 90240 Oulu, Finland",
      "endTimeGmt": "2020-04-28T04:40:55Z",
      "classificationType": 0
    }
  ],
  "metadata": {
    "from": "2020-04-24",
    "to": "2020-05-01"
  }
}

```

## trip.json

```json
{
  "tripEvents": [
    {
      "lat": 65.5749144,
      "lon": 28.2446904,
      "overspeed": false,
      "highway": false,
      "isEv": true
    },
    {
      "lat": 65.5749001,
      "lon": 28.24468,
      "overspeed": false,
      "highway": false,
      "isEv": true
    },
    {
      "lat": 65.5746601,
      "lon": 28.24442,
      "overspeed": false,
      "highway": false,
      "isEv": true
    },
    {
      "lat": 65.5745756,
      "lon": 28.2446923,
      "overspeed": false,
      "highway": false,
      "isEv": true
    },
    {
      "lat": 65.5744982,
      "lon": 28.2449416,
      "overspeed": false,
      "highway": false,
      "isEv": true
    },
    {
      "lat": 65.5743252,
      "lon": 28.2454992,
      "overspeed": false,
      "highway": false,
      "isEv": true
    },
    {
      "lat": 65.5742864,
      "lon": 28.245624,
      "overspeed": false,
      "highway": false,
      "isEv": false
    },
    {
      "lat": 65.5741201,
      "lon": 28.24616,
      "overspeed": false,
      "highway": false,
      "isEv": false
    },
    {
      "lat": 65.5740024,
      "lon": 28.2465377,
      "overspeed": false,
      "highway": false,
      "isEv": false
    },
    {
      "lat": 65.5738801,
      "lon": 28.24693,
      "overspeed": false,
      "highway": false,
      "isEv": false
    },
    {
      "lat": 65.5738101,
      "lon": 28.24715,
      "overspeed": false,
      "highway": false,
      "isEv": false
    },
    {
      "lat": 65.5737401,
      "lon": 28.24739,
      "overspeed": false,
      "highway": false,
      "isEv": false
    },
    {
      "lat": 65.5737229,
      "lon": 28.2474588,
      "overspeed": false,
      "highway": false,
      "isEv": false
    },
    {
      "lat": 65.5737001,
      "lon": 28.24755,
      "overspeed": false,
      "highway": false,
      "isEv": false
    },
    {
      "lat": 65.5736701,
      "lon": 28.24768,
      "overspeed": false,
      "highway": false,
      "isEv": false
    },
    {
      "lat": 65.5736501,
      "lon": 28.2478,
      "overspeed": false,
      "highway": false,
      "isEv": false
    },
    {
      "lat": 65.5736401,
      "lon": 28.24791,
      "overspeed": false,
      "highway": false,
      "isEv": false
    },
    {
      "lat": 65.5736401,
      "lon": 28.248019,
      "overspeed": false,
      "highway": false,
      "isEv": false
    },
    {
      "lat": 65.5736401,
      "lon": 28.24804,
      "overspeed": false,
      "highway": false,
      "isEv": false
    },
    {
      "lat": 65.5736501,
      "lon": 28.24818,
      "overspeed": false,
      "highway": false,
      "isEv": false
    },
    {
      "lat": 65.5736801,
      "lon": 28.24844,
      "overspeed": false,
      "highway": false,
      "isEv": false
    },
    {
      "lat": 65.5735695,
      "lon": 28.2485229,
      "overspeed": false,
      "highway": false,
      "isEv": false
    },
    {
      "lat": 65.5734597,
      "lon": 28.2486053,
      "overspeed": false,
      "highway": false,
      "isEv": false
    },
    {
      "lat": 65.5733201,
      "lon": 28.24871,
      "overspeed": false,
      "highway": false,
      "isEv": false
    },
    {
      "lat": 65.5731901,
      "lon": 28.24881,
      "overspeed": false,
      "highway": false,
      "isEv": false
    },
    {
      "lat": 65.5730901,
      "lon": 28.24889,
      "overspeed": false,
      "highway": false,
      "isEv": false
    },
    {
      "lat": 65.5730001,
      "lon": 28.24899,
      "overspeed": false,
      "highway": false,
      "isEv": false
    },
    {
      "lat": 65.5728901,
      "lon": 28.24912,
      "overspeed": false,
      "highway": false,
      "isEv": false
    },
    {
      "lat": 65.5728001,
      "lon": 28.2492699,
      "overspeed": false,
      "highway": false,
      "isEv": false
    },
    {
      "lat": 65.572773,
      "lon": 28.2493271,
      "overspeed": false,
      "highway": false,
      "isEv": false
    },
    {
      "lat": 65.5727101,
      "lon": 28.24946,
      "overspeed": false,
      "highway": false,
      "isEv": false
    },
    {
      "lat": 65.5726615,
      "lon": 28.2495717,
      "overspeed": false,
      "highway": false,
      "isEv": false
    },
    {
      "lat": 65.572528,
      "lon": 28.2498788,
      "overspeed": false,
      "highway": false,
      "isEv": false
    },
    {
      "lat": 65.5725101,
      "lon": 28.2499199,
      "overspeed": false,
      "highway": false,
      "isEv": false
    },
    {
      "lat": 65.5725724,
      "lon": 28.2500616,
      "overspeed": false,
      "highway": false,
      "isEv": false
    },
    {
      "lat": 65.5728001,
      "lon": 28.2505799,
      "overspeed": false,
      "highway": false,
      "isEv": false
    },
    {
      "lat": 65.5728242,
      "lon": 28.2506384,
      "overspeed": false,
      "highway": false,
      "isEv": false
    },
    {
      "lat": 65.5728701,
      "lon": 28.25075,
      "overspeed": false,
      "highway": false,
      "isEv": false
    },
    {
      "lat": 65.5731201,
      "lon": 28.2513399,
      "overspeed": false,
      "highway": false,
      "isEv": false
    },
    {
      "lat": 65.5732301,
      "lon": 28.2516,
      "overspeed": false,
      "highway": false,
      "isEv": false
    },
    {
      "lat": 65.5732571,
      "lon": 28.251665,
      "overspeed": false,
      "highway": false,
      "isEv": false
    },
    {
      "lat": 65.5735501,
      "lon": 28.2523699,
      "overspeed": false,
      "highway": false,
      "isEv": false
    },
    {
      "lat": 65.5749601,
      "lon": 28.2556899,
      "overspeed": false,
      "highway": false,
      "isEv": false
    },
    {
      "lat": 65.5752587,
      "lon": 28.2563954,
      "overspeed": false,
      "highway": false,
      "isEv": false
    },
    {
      "lat": 65.5757748,
      "lon": 28.2576148,
      "overspeed": false,
      "highway": false,
      "isEv": false
    },
    {
      "lat": 65.5758701,
      "lon": 28.2578399,
      "overspeed": false,
      "highway": false,
      "isEv": false
    },
    {
      "lat": 65.5763001,
      "lon": 28.2588499,
      "overspeed": false,
      "highway": false,
      "isEv": false
    },
    {
      "lat": 65.5763563,
      "lon": 28.2589816,
      "overspeed": false,
      "highway": false,
      "isEv": false
    },
    {
      "lat": 65.5777481,
      "lon": 28.2622431,
      "overspeed": false,
      "highway": false,
      "isEv": true
    },
    {
      "lat": 65.5783288,
      "lon": 28.2636042,
      "overspeed": false,
      "highway": false,
      "isEv": true
    },
    {
      "lat": 65.5785913,
      "lon": 28.2642195,
      "overspeed": false,
      "highway": false,
      "isEv": true
    },
    {
      "lat": 65.5788205,
      "lon": 28.2647567,
      "overspeed": false,
      "highway": false,
      "isEv": false
    },
    {
      "lat": 65.5790002,
      "lon": 28.2651779,
      "overspeed": false,
      "highway": false,
      "isEv": true
    },
    {
      "lat": 65.5790626,
      "lon": 28.2653242,
      "overspeed": false,
      "highway": false,
      "isEv": true
    },
    {
      "lat": 65.5792101,
      "lon": 28.2656699,
      "overspeed": false,
      "highway": false,
      "isEv": true
    },
    {
      "lat": 65.5793601,
      "lon": 28.2652699,
      "overspeed": false,
      "highway": false,
      "isEv": true
    },
    {
      "lat": 65.5793601,
      "lon": 28.2652699,
      "overspeed": false,
      "highway": false,
      "isEv": true
    },
    {
      "lat": 65.5793601,
      "lon": 28.2652699,
      "overspeed": false,
      "highway": false,
      "isEv": true
    }
  ],
  "tripEventsType": [],
  "statistics": {
    "totalDurationInSec": 126,
    "idleDurationInSec": 6,
    "highwayDurationInSec": 0,
    "overspeedDurationInSec": 0,
    "fuelConsumptionInL": 0.137,
    "maxSpeedInKmph": 85,
    "averageSpeedInKmph": 42.2,
    "totalDistanceInKm": 1.477,
    "highwayDistanceInKm": 0,
    "overspeedDistanceInKm": 0,
    "countriesVisited": [
      "FI"
    ],
    "hardaccs": 0,
    "hardbrakes": 0,
    "totalDistanceInMiles": 0.92,
    "averageSpeedInMph": 26.23,
    "maxSpeedInMph": 52.83
  }
}
```

## parking.json
- address field is not being updated since July 2020. See parking address from latest trip endAddress instead.
```json
{
  "event": {
    "lat": "64.7704251",
    "lon": "25.6604713",
    "address": "Taivalkoski Teboil, 93400 Taivalkoski, Finland",
    "timestamp": "1588178253000"
  },
  "tripStatus": "0"
}
```

## mileage.json

```json
[
  {
    "type": "mileage",
    "value": 3205,
    "unit": "km"
  },
  {
    "type": "Fuel",
    "value": 22
  }
]
```

## remote_control.json
```json
{
  "ReturnCode": "000000",
  "VehicleInfo": {
    "AcquisitionDatetime": "2020-10-17T06:08:36Z",
    "ChargeInfo": {
      "BatteryPowerSupplyPossibleTime": 16383,
      "ChargeEndTime": "00:00",
      "ChargeRemainingAmount": 100,
      "ChargeStartTime": "22:10",
      "ChargeType": 1,
      "ChargeWeek": 5,
      "ChargingStatus": "chargeComplete",
      "ConnectorStatus": 5,
      "EvDistanceInKm": 79.9,
      "EvDistanceWithAirCoInKm": 73.51,
      "EvTravelableDistance": 79.9,
      "EvTravelableDistanceSubtractionRate": 8,
      "PlugInHistory": 33,
      "PlugStatus": 45,
      "RemainingChargeTime": 65535,
      "SettingChangeAcceptanceStatus": 0
    },
    "RemoteHvacInfo": {
      "BlowerStatus": 0,
      "FrontDefoggerStatus": 0,
      "InsideTemperature": 22,
      "LatestAcStartTime": "2020-10-16T03:50:15Z",
      "RearDefoggerStatus": 0,
      "RemoteHvacMode": 0,
      "RemoteHvacProhibitionSignal": 1,
      "SettingTemperature": 21,
      "TemperatureDisplayFlag": 0,
      "Temperaturelevel": 29
    }
  }
}
```
