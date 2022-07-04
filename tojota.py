# Copyright 2020 Janne Määttä
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
"""
MyT interaction library
"""
import glob
import json
import logging
import os
from pathlib import Path
import platform
import sys

import pendulum
import requests

logging.basicConfig(format='%(asctime)s:%(name)s:%(levelname)s: %(message)s')
log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)

# Fake app version mimicking the Android app
APP_VERSION = '4.10.0'

CACHE_DIR = 'cache'
USER_DATA = 'user_data.json'
INFLUXDB_URL = 'http://localhost:8086/write?db=tojota'


class Myt:
    """
    Class for interacting with Toyota vehicle API
    """
    def __init__(self):
        """
        Create cache directory, try to load existing user data or if it doesn't exists do login.
        """
        os.makedirs(CACHE_DIR, exist_ok=True)
        self.config_data = self._get_config()
        self.user_data = self._get_user_data()
        if self.user_data:
            self.headers = {'X-TME-TOKEN': self.user_data['token'], 'X-TME-LOCALE': 'fi-fi'}
        else:
            self.login()

    @staticmethod
    def _get_config(config_file='myt.json'):
        """
        Load configuration values from config file. Return config as a dict.
        :param config_file: Filename on configs directory
        :return: dict
        """
        with open(Path('configs')/config_file) as f:
            try:
                config_data = json.load(f)
            except Exception as e:  # pylint: disable=W0703
                log.error('Failed to load configuration JSON! %s', str(e))
                raise
        return config_data

    @staticmethod
    def _get_user_data():
        """
        Try to load existing user data from CACHE_DIR. If it doesn't exists or is malformed return None
        :return: user_data dict or None
        """
        try:
            with open(Path(CACHE_DIR) / USER_DATA, encoding='utf-8') as f:
                try:
                    user_data = json.load(f)
                except Exception as e:  # pylint: disable=W0703
                    log.error('Failed to load cached user data JSON! %s', str(e))
                    raise
            return user_data
        except FileNotFoundError:
            return None

    @staticmethod
    def _read_file(file_path):
        """
        Load file contents or return None if loading fails
        :param file_path: Path for a file
        :return: File contents
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return f.read()
        except (FileNotFoundError, TypeError):
            return None

    @staticmethod
    def _write_file(file_path, contents):
        """
        Write string to a file
        :param file_path: Path for a file
        :param contents: String to be written
        :return:
        """
        if platform.system() == 'Windows':
            file_path = str(file_path).replace(':', '')
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(contents)

    @staticmethod
    def _find_latest_file(path):
        """
        Return latest file with given path pattern or None if not found
        :param path: Path expression for directory contents. Like 'cache/trips/trips*'
        :return: Latest file path or None if not found
        """
        files = glob.glob(path)
        if files:
            return max(files, key=os.path.getctime)
        return None

    def login(self, locale='fi-fi'):
        """
        Do Toyota SSO login. Saves user data for configured account in self.user_data and sets token to self.headers.
        User data is saved to CACHE_DIR for reuse.
        :param locale: Locale for login is required but doesn't seem to have any effect
        :return: None
        """
        login_headers = {'X-TME-BRAND': 'TOYOTA', 'X-TME-LC': locale, 'Accept': 'application/json, text/plain, */*',
                         'Sec-Fetch-Dest': 'empty'}
        log.info('Logging in...')
        r = requests.post('https://ssoms.toyota-europe.com/authenticate', headers=login_headers, json=self.config_data)
        if r.status_code != 200:
            raise ValueError('Login failed, check your credentials! {}'.format(r.text))
        user_data = r.json()
        self.user_data = user_data
        self.headers = {'X-TME-TOKEN': user_data['token']}
        self._write_file(Path(CACHE_DIR) / USER_DATA, r.text)

    def get_trips(self, trip=1):
        """
        Get latest 10 trips. Save trips to CACHE_DIR/trips/trips-`datetime` file. Will save every time there is a new
        trip or daily because of changing metadata if no new trips. Saved information is not currently used for
        anything.
        :param trip: There is paging, but it doesn't seem to do anything. 1 is the default value.
        :return: recentTrips dict, fresh boolean True is new data was fetched
        """
        fresh = False
        trips_path = Path(CACHE_DIR) / 'trips'
        trips_file = trips_path / 'trips-{}'.format(pendulum.now())
        log.info('Fetching trips...')
        r = requests.get(
            'https://cpb2cs.toyota-europe.com/api/user/{}/cms/trips/v2/history/vin/{}/{}'.format(
                self.user_data['customerProfile']['uuid'], self.config_data['vin'], trip), headers=self.headers)
        if r.status_code != 200:
            raise ValueError('Failed to get data, Status: {} Headers: {} Body: {}'.format(r.status_code, r.headers,
                                                                                          r.text))
        os.makedirs(trips_path, exist_ok=True)
        previous_trip = self._read_file(self._find_latest_file(str(trips_path / 'trips*')))
        if r.text != previous_trip:
            self._write_file(trips_file, r.text)
            fresh = True
        trips = r.json()
        return trips, fresh

    def get_trip(self, trip_id):
        """
        Get trip info. Trip is identified by uuidv4. Save trip data to CACHE_DIR/trips/[12]/[34]/uuid file. If given
        trip already exists in CACHE_DIR just get it from there.
        :param trip_id: tripId to fetch. uuid v4 that is received from get_trips().
        :return: trip dict, fresh boolean True is new data was fetched
        """
        fresh = False
        trip_base_path = Path(CACHE_DIR) / 'trips'
        trip_path = trip_base_path / trip_id[0:2] / trip_id[2:4]
        trip_file = trip_path / trip_id
        if not trip_file.exists():
            log.debug('Fetching trip...')
            r = requests.get('https://cpb2cs.toyota-europe.com/api/user/{}/cms/trips/v2/{}/events/vin/{}'.format(
                self.user_data['customerProfile']['uuid'], trip_id, self.config_data['vin']), headers=self.headers)
            if r.status_code != 200:
                raise ValueError('Failed to get data {} {}'.format(r.status_code, r.headers))
            os.makedirs(trip_path, exist_ok=True)
            self._write_file(trip_file, r.text)
            trip_data = r.json()
            fresh = True
        else:
            with open(trip_file, encoding='utf-8') as f:
                trip_data = json.load(f)
        return trip_data, fresh

    def get_parking(self):
        """
        Get location information. Location is saved when vehicle is powered off. Save data to
        CACHE_DIR/parking/parking-`datetime` file. Saved information is not currently used for anything. When vehicle
        is powered on again tripStatus will change to '1'.
        :return: Location dict, fresh Boolean if new data was fetched
        """
        fresh = False
        parking_path = Path(CACHE_DIR) / 'parking'
        parking_file = parking_path / 'parking-{}'.format(pendulum.now())
        token = self.user_data['token']
        uuid = self.user_data['customerProfile']['uuid']
        vin = self.config_data['vin']
        headers = {'Cookie': f'iPlanetDirectoryPro={token}', 'VIN': vin}
        url = f'https://myt-agg.toyota-europe.com/cma/api/users/{uuid}/vehicle/location'
        r = requests.get(url, headers=headers)
        if r.status_code != 200:
            raise ValueError('Failed to get data {} {} {}'.format(r.text, r.status_code, r.headers))
        os.makedirs(parking_path, exist_ok=True)
        previous_parking = self._read_file(self._find_latest_file(str(parking_path / 'parking*')))
        if r.text != previous_parking:
            self._write_file(parking_file, r.text)
            fresh = True
        return r.json(), fresh

    def get_odometer_fuel(self):
        """
        Get mileage and fuel tank information. Data is saved when vehicle is powered off. Save data to
        CACHE_DIR/odometer/odometer-`datetime` file.
        :return: list(odometer, odometer_unit, fuel_percentage, fresh)
        """
        fresh = False
        odometer_path = Path(CACHE_DIR) / 'odometer'
        odometer_file = odometer_path / 'odometer-{}'.format(pendulum.now())
        token = self.user_data['token']
        vin = self.config_data['vin']
        uuid = self.user_data['customerProfile']['uuid']
        headers = {'Cookie': f'iPlanetDirectoryPro={token}', 'X-TME-APP-VERSION': APP_VERSION, 'UUID': uuid}
        url = f'https://myt-agg.toyota-europe.com/cma/api/vehicle/{vin}/addtionalInfo'  # (sic)
        r = requests.get(url, headers=headers)
        if r.status_code != 200:
            raise ValueError('Failed to get data {} {} {}'.format(r.text, r.status_code, r.headers))
        os.makedirs(odometer_path, exist_ok=True)
        previous_odometer = self._read_file(self._find_latest_file(str(odometer_path / 'odometer*')))
        if r.text != previous_odometer:
            self._write_file(odometer_file, r.text)
            fresh = True
        data = r.json()
        odometer = 0
        odometer_unit = ''
        fuel = 0
        for item in data:
            if item['type'] == 'mileage':
                odometer = item['value']
                odometer_unit = item['unit']
            if item['type'] == 'Fuel':
                fuel = item['value']
        return odometer, odometer_unit, fuel, fresh

    def get_remote_control_status(self):
        """
        Get location information. Location is saved when vehicle is powered off. Save data to
        CACHE_DIR/remote_control/remote_control-`datetime` file.
        :return: Location dict, fresh Boolean if new data was fetched
        """
        fresh = False
        remote_control_path = Path(CACHE_DIR) / 'remote_control'
        remote_control_file = remote_control_path / 'remote_control-{}'.format(pendulum.now())
        token = self.user_data['token']
        uuid = self.user_data['customerProfile']['uuid']
        vin = self.config_data['vin']
        headers = {'Cookie': f'iPlanetDirectoryPro={token}', 'uuid': uuid, 'X-TME-LOCALE': 'fi-fi'}
        url = f'https://myt-agg.toyota-europe.com/cma/api/vehicles/{vin}/remoteControl/status'
        r = requests.get(url, headers=headers)
        if r.status_code != 200:
            raise ValueError('Failed to get data {} {} {}'.format(r.text, r.status_code, r.headers))
        data = r.json()
        os.makedirs(remote_control_path, exist_ok=True)

        # remoteControl/status messages has varying order of the content, load it as a dict for comparison
        try:
            previous_remote_control = json.loads(self._read_file(self._find_latest_file(str(
                remote_control_path / 'remote_control*'))))
        except TypeError:
            previous_remote_control = None

        if data != previous_remote_control:
            self._write_file(remote_control_file, json.dumps(r.json(), sort_keys=True))
            fresh = True
        return data, fresh

    def get_driving_statistics(self, date_from=None, interval='day', locale='fi-fi'):
        """
        Get driving statistics information. Save data to
        CACHE_DIR/statistics/statistics-`datetime` file.

        :param: interval 'day' 'week', if interval is None, yearly statistics are returned (set date_from -365 days)
        :param: date_from '2020-11-01', max -60 days for Day Interval and max -120 days for Week Interval
        :param: locale 'en-us', no visible effects but required
        :return: statistics dict, fresh Boolean if new data was fetched
        """
        fresh = False
        statistics_path = Path(CACHE_DIR) / 'statistics'
        statistics_file = statistics_path / 'statistics-{}'.format(pendulum.now())
        token = self.user_data['token']
        uuid = self.user_data['customerProfile']['uuid']
        vin = self.config_data['vin']
        headers = {'Cookie': f'iPlanetDirectoryPro={token}', 'uuid': uuid, 'vin': vin, 'X-TME-BRAND': 'TOYOTA',
                   'X-TME-LOCALE': locale}
        url = 'https://myt-agg.toyota-europe.com/cma/api/v2/trips/summarize'
        params = {'from': date_from, 'calendarInterval': interval}
        r = requests.get(url, headers=headers, params=params)
        if r.status_code != 200:
            raise ValueError('Failed to get data {} {} {}'.format(r.text, r.status_code, r.headers))
        data = r.json()
        os.makedirs(statistics_path, exist_ok=True)

        try:
            previous_statistics = json.loads(self._read_file(self._find_latest_file(str(
                statistics_path / 'statistics*'))))
        except TypeError:
            previous_statistics = None

        if data != previous_statistics:
            self._write_file(statistics_file, json.dumps(r.json(), sort_keys=True))
            fresh = True

        return data, fresh


def insert_into_influxdb(measurement, value):
    """
    Insert data into influxdb (without authentication)
    :param measurement: Measurement name
    :param value: Measurement value
    :return: null
    """
    headers = {'Content-Type': 'application/x-www-form-urlencoded'}
    payload = "{} value={}".format(measurement, value)
    requests.post(INFLUXDB_URL, headers=headers, data=payload)


def remote_control_to_db(myt, fresh, charge_info, hvac_info):
    if fresh and myt.config_data['use_influxdb']:
        log.debug('Saving remote control data to influxdb')
        insert_into_influxdb('charge_level', charge_info['ChargeRemainingAmount'])
        insert_into_influxdb('ev_range', charge_info['EvDistanceWithAirCoInKm'])
        insert_into_influxdb('charge_type', charge_info['ChargeType'])
        insert_into_influxdb('charge_week', charge_info['ChargeWeek'])
        insert_into_influxdb('connector_status', charge_info['ConnectorStatus'])
        insert_into_influxdb('subtraction_rate', charge_info['EvTravelableDistanceSubtractionRate'])
        insert_into_influxdb('plugin_history', charge_info['PlugInHistory'])
        insert_into_influxdb('plugin_status', charge_info['PlugStatus'])
        insert_into_influxdb('hv_range', charge_info['GasolineTravelableDistance'])

        insert_into_influxdb('temperature_inside', hvac_info['InsideTemperature'])
        insert_into_influxdb('temperature_setting', hvac_info['SettingTemperature'])
        insert_into_influxdb('temperature_level', hvac_info['Temperaturelevel'])


def odometer_to_db(myt, fresh, fuel_percent, odometer):
    if fresh and myt.config_data['use_influxdb']:
        log.debug('Saving odometer data to influxdb')
        insert_into_influxdb('odometer', odometer)
        insert_into_influxdb('fuel_level', fuel_percent)


def trip_data_to_db(myt, fresh, average_consumption, stats):
    if fresh and myt.config_data['use_influxdb']:
        insert_into_influxdb('trip_kilometers', stats['totalDistanceInKm'])
        insert_into_influxdb('trip_liters', stats['fuelConsumptionInL'])
        insert_into_influxdb('trip_average_consumption', average_consumption)


def main():
    """
    Get trips, get parking information, get trips information
    :return:
    """
    myt = Myt()

    # Try to fetch trips array with existing user_info. If it fails, do new login and try again.
    try:
        trips, fresh = myt.get_trips()
    except ValueError:
        log.info('Failed to use cached token, doing fresh login...')
        myt.login()
        trips, fresh = myt.get_trips()
    try:
        latest_address = trips['recentTrips'][0]['endAddress']
    except (KeyError, IndexError):
        latest_address = 'Unknown address'

    # Check is vehicle is still parked or moving and print corresponding information. Parking timestamp is epoch
    # timestamp with microseconds. Actual value seems to be at second precision level.
    log.info('Get parking info...')
    try:
        parking, fresh = myt.get_parking()
        if parking['tripStatus'] == '0':
            print('Car is parked at {} at {}'.format(latest_address,
                                                     pendulum.from_timestamp(int(parking['event']['timestamp']) / 1000).
                                                     in_tz(myt.config_data['timezone']).to_datetime_string()))
        else:
            print('Car left from {} parked at {}'.format(latest_address,
                                                         pendulum.from_timestamp(int(parking['event']['timestamp']) /
                                                                                 1000).
                                                         in_tz(myt.config_data['timezone']).to_datetime_string()))
    except ValueError:
        print('Didn\'t get parking information!')

    # Get odometer and fuel tank status
    log.info('Get odometer info...')
    try:
        odometer, odometer_unit, fuel_percent, fresh = myt.get_odometer_fuel()
        print('Odometer {} {}, {}% fuel left'.format(odometer, odometer_unit, fuel_percent))
        odometer_to_db(myt, fresh, fuel_percent, odometer)
    except ValueError:
        print('Didn\'t get odometer information!')

    # Get remote control status
    if myt.config_data['use_remote_control']:
        log.info('Get remote control status...')
        status, fresh = myt.get_remote_control_status()
        charge_info = status['VehicleInfo']['ChargeInfo']
        hvac_info = status['VehicleInfo']['RemoteHvacInfo']
        print('Battery level {}%, EV range {} km, HV range {} km, Inside temperature {}, Charging status {}, status reported at {}'.
              format(charge_info['ChargeRemainingAmount'], charge_info['EvDistanceWithAirCoInKm'],
                     charge_info['GasolineTravelableDistance'],
                     hvac_info['InsideTemperature'], charge_info['ChargingStatus'],
                     pendulum.parse(status['VehicleInfo']['AcquisitionDatetime']).
                     in_tz(myt.config_data['timezone']).to_datetime_string()
                     ))
        if charge_info['ChargingStatus'] == 'charging' and charge_info['RemainingChargeTime'] != 65535:
            acquisition_datetime = pendulum.parse(status['VehicleInfo']['AcquisitionDatetime'])
            charging_end_time = acquisition_datetime.add(minutes=charge_info['RemainingChargeTime'])
            print('Charging will be completed at {}'.format(charging_end_time.in_tz(myt.config_data['timezone']).
                                                            to_datetime_string()))
        if hvac_info['RemoteHvacMode']:
            front = 'On' if hvac_info['FrontDefoggerStatus'] else 'Off'
            rear = 'On' if hvac_info['RearDefoggerStatus'] else 'Off'

            print('HVAC is on since {}. Remaining heating time {} minutes. Windscreen heating is {}, rear window heating is {}.'.format(
                pendulum.parse(hvac_info['LatestAcStartTime']).in_tz(myt.config_data['timezone']).to_datetime_string(),
                hvac_info['RemainingMinutes'], front, rear))

        remote_control_to_db(myt, fresh, charge_info, hvac_info)

    # Get detailed information about trips and calculate cumulative kilometers and fuel liters
    kms = 0
    ls = 0
    fresh_data = 0
    for trip in trips['recentTrips']:
        trip_data, fresh = myt.get_trip(trip['tripId'])
        fresh_data += fresh
        stats = trip_data['statistics']
        # Parse UTC datetime strings to local time
        start_time = pendulum.parse(trip['startTimeGmt']).in_tz(myt.config_data['timezone']).to_datetime_string()
        end_time = pendulum.parse(trip['endTimeGmt']).in_tz(myt.config_data['timezone']).to_datetime_string()
        # Remove country part from address strings
        try:
            start = trip['startAddress'].split(',')
        except KeyError:
            start = ['Unknown', ' Unknown']
        try:
            end = trip['endAddress'].split(',')
        except KeyError:
            end = ['Unknown', ' Unknown']
        try:
            start_address = '{},{}'.format(start[0], start[1])
        except IndexError:
            start_address = start[0]
        try:
            end_address = '{},{}'.format(end[0], end[1])
        except IndexError:
            end_address = end[0]
        kms += stats['totalDistanceInKm']
        ls += stats['fuelConsumptionInL']
        average_consumption = (stats['fuelConsumptionInL']/stats['totalDistanceInKm'])*100
        trip_data_to_db(myt, fresh, average_consumption, stats)
        print('{} {} -> {} {}: {} km, {} km/h, {:.2f} l/100 km, {:.2f} l'.
              format(start_time, start_address, end_time, end_address, stats['totalDistanceInKm'],
                     stats['averageSpeedInKmph'], average_consumption, stats['fuelConsumptionInL']))
    if fresh_data and myt.config_data['use_influxdb']:
        insert_into_influxdb('short_term_average_consumption', (ls/kms)*100)
    print('Total distance: {:.3f} km, Fuel consumption: {:.2f} l, {:.2f} l/100 km'.format(kms, ls, (ls/kms)*100))


if __name__ == "__main__":
    sys.exit(main())
