# Library for handling Toyota vehicle API

Unofficial python functions for handling data from Toyota Connected services APIs. https://www.toyota-europe.com/myt,
https://play.google.com/store/apps/details?id=app.mytoyota.toyota.com.mytoyota

# Installation

- Create virtual environment
- On Windows platform run `pip install pip==18.1` because of [pendulum bug](https://github.com/sdispater/pendulum/issues/454)
- Install requirements `pip install -r requirements.txt`

# Usage

- Configure your MyT user account, password and vehicle VIN into `configs/myt.json`
- Run `python tojota.py` to fetch, save and print data
- Data is saved to cache directory for further usage

# Example data

## trips.json

```
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

```
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

```
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

```
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
