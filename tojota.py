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
from urllib.parse import parse_qs, urlparse

import jwt
import pendulum
import requests

logging.basicConfig(format='%(asctime)s:%(name)s:%(levelname)s: %(message)s')
log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)

CACHE_DIR = 'cache'
USER_DATA = 'user_data.json'
INFLUXDB_URL = 'http://localhost:8086/write?db=tojota'

MYT_API_URL = 'https://ctpa-oneapi.tceu-ctp-prd.toyotaconnectedeurope.io'


class Myt:
    """
    Class for interacting with Toyota vehicle API
    """
    def __init__(self):
        """
        Create cache directory, try to load existing user data or if it doesn't exist do login.
        """
        os.makedirs(CACHE_DIR, exist_ok=True)
        self.config_data = self._get_config()
        self.user_data = self._get_user_data()
        if not self.user_data or pendulum.now() > pendulum.parse(self.user_data['expiration']):
            self.login()

        self.headers = {
            'Authorization': f'Bearer {self.user_data["access_token"]}',
            'x-api-key': 'tTZipv6liF74PwMfk9Ed68AQ0bISswwf3iHQdqcF',  # Found from the intternets
            'x-guid': self.user_data['uuid'],
            'guid': self.user_data['uuid'],
            'vin': self.config_data['vin'],
            "x-brand": "T",
        }

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
            return []

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

    def login(self):
        """
        Do Toyota SSO login. Saves user data for configured account in self.user_data
        User data is saved to CACHE_DIR for reuse.
        :return: None
        """
        login_url = 'https://b2c-login.toyota-europe.com/json/realms/root/realms/tme/authenticate?authIndexType=service&authIndexValue=oneapp'
        authorize_url = 'https://b2c-login.toyota-europe.com/oauth2/realms/root/realms/tme/authorize?client_id=oneapp&scope=openid+profile+write&response_type=code&redirect_uri=com.toyota.oneapp:/oauth2Callback&code_challenge=plain&code_challenge_method=plain'
        token_url = 'https://b2c-login.toyota-europe.com/oauth2/realms/root/realms/tme/access_token'

        if "refresh_token" not in self.user_data:
            login_headers = {'Content-Type': 'application/json'}
            log.info('Get initial auth_id...')
            r = requests.post(login_url, headers=login_headers)
            log.info('Get username prompt...')
            r = requests.post(login_url, headers=login_headers, data=r.text)
            data = r.json()
            data['callbacks'][0]['input'][0]['value'] = self.config_data['username']
            log.info('Get password prompt...')
            r = requests.post(login_url, headers=login_headers, data=json.dumps(data))
            data = r.json()
            try:
                data['callbacks'][0]['input'][0]['value'] = self.config_data['password']
            except KeyError:
                raise ValueError('Login failed, check your username! {}'.format(data['callbacks'][0]['output'][0]['value']))
            log.info('Get login token...')
            r = requests.post(login_url, headers=login_headers, data=json.dumps(data))
            if r.status_code != 200:
                raise ValueError('Login failed, check your password! {}'.format(r.text))
            data = r.json()

            log.info('Authorizing...')
            headers = {'cookie': f"iPlanetDirectoryPro={data['tokenId']}"}
            r = requests.get(authorize_url, headers=headers, allow_redirects=False)
            authentication_code = parse_qs(urlparse(r.headers['Location']).query)['code'][0]

            log.info('Get access tokens...')
            headers = {"authorization": "basic b25lYXBwOm9uZWFwcA=="}  # oneapp:oneapp
            data = {
                'client_id': 'oneapp',
                'code': authentication_code,
                'redirect_uri': 'com.toyota.oneapp:/oauth2Callback',
                'grant_type': 'authorization_code',
                'code_verifier': 'plain',
            }
            r = requests.post(token_url, headers=headers, data=data, allow_redirects=False)
            if not r.ok:
                raise ValueError('Getting authorization tokens failed! {}'.format(r.text))
        else:
            log.info('Using refresh token...')
            headers = {"authorization": "basic b25lYXBwOm9uZWFwcA=="}  # oneapp:oneapp
            data = {
                'client_id': 'oneapp',
                'refresh_token': self.user_data['refresh_token'],
                'redirect_uri': 'com.toyota.oneapp:/oauth2Callback',
                'grant_type': 'refresh_token',
                'code_verifier': 'plain',
            }
            r = requests.post(token_url, headers=headers, data=data, allow_redirects=False)
            if not r.ok:
                raise ValueError('Getting authorization tokens using refresh token failed! {}'.format(r.text))

        user_data = r.json()
        user_data['uuid'] = jwt.decode(
            user_data['id_token'],
            algorithms=['RS256'],
            options={'verify_signature': False},
            audience='oneappsdkclient',
        )['uuid']
        user_data['expiration'] = str(pendulum.now().add(seconds=user_data['expires_in']))

        self.user_data = user_data
        self._write_file(Path(CACHE_DIR) / USER_DATA, json.dumps(user_data))

    def get_trips(self, from_date=None, to_date=None, route=False, summary=True, limit=50, offset=0):
        """
        Get latest 10 trips. Save trips to CACHE_DIR/trips/trips-`datetime` file. Will save every time there is a new
        trip or daily because of changing metadata if no new trips. Saved information is not currently used for
        anything.
        :param from_date: start date
        :param to_date: end date
        :param route: Get route location points
        :param summary: Include summary data
        :param limit: Limit trip count. Max 50 with routes, max 1000 without routes
        :param offset: Pagination offset
        :return: recentTrips dict, fresh boolean True if different data was fetched than previously
        """
        fresh = False
        trips_path = Path(CACHE_DIR) / 'trips'
        trips_file = trips_path / 'trips-{}'.format(pendulum.now())
        log.info('Fetching trips...')
        if not to_date:
            to_date = pendulum.now().to_date_string()
        if not from_date:
            from_date = pendulum.now().add(weeks=-1).to_date_string()
        r = requests.get(
            f'{MYT_API_URL}/v1/trips?from={from_date}&to={to_date}&route={route}&summary={summary}&limit={limit}&offset={offset}',
            headers=self.headers)
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

    def get_trip(self, trips, trip_id):
        """
        Get trip info. Trip is identified by uuidv4. Save trip data to CACHE_DIR/trips/[12]/[34]/uuid file. If given
        trip already exists in CACHE_DIR just get it from there.
        :param trips: trips data structure
        :param trip_id: tripId to fetch. uuid v4 that is received from get_trips().
        :return: trip dict, fresh boolean True is new data was fetched
        """
        fresh = False
        trip_base_path = Path(CACHE_DIR) / 'trips'
        trip_path = trip_base_path / trip_id[0:2] / trip_id[2:4]
        trip_file = trip_path / trip_id
        if not trip_file.exists():
            log.debug('Fetching trip...')
            for trip in trips:
                if trip['id'] == trip_id:
                    trip_data = trip
                    break
            else:
                raise ValueError('Failed to find the trip!')

            os.makedirs(trip_path, exist_ok=True)
            self._write_file(trip_file, json.dumps(trip_data))
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
        url = f'{MYT_API_URL}/v1/location'
        r = requests.get(url, headers=self.headers)
        if r.status_code != 200:
            raise ValueError('Failed to get data {} {} {}'.format(r.text, r.status_code, r.headers))
        os.makedirs(parking_path, exist_ok=True)
        previous_parking = self._read_file(self._find_latest_file(str(parking_path / 'parking*')))
        if r.text != previous_parking:
            self._write_file(parking_file, r.text)
            fresh = True
        return r.json(), fresh

    def get_telemetry(self):
        """
        Get mileage and range information. Data is saved when vehicle is powered off. Save data to
        CACHE_DIR/odometer/odometer-`datetime` file.
        :return: dict(odometer, hv_percentage, hv_range, ev_percentage, timestamp, charging_status), fresh
        """
        fresh = False
        odometer_path = Path(CACHE_DIR) / 'odometer'
        odometer_file = odometer_path / 'odometer-{}'.format(pendulum.now())
        url = f'{MYT_API_URL}/v3/telemetry'
        r = requests.get(url, headers=self.headers)

        if r.status_code != 200:
            raise ValueError('Failed to get data {} {} {}'.format(r.text, r.status_code, r.headers))
        os.makedirs(odometer_path, exist_ok=True)
        previous_odometer = self._read_file(self._find_latest_file(str(odometer_path / 'odometer*')))
        if r.text != previous_odometer:
            self._write_file(odometer_file, r.text)
            fresh = True
        data = r.json()['payload']
        telemetry = {
            'odometer': data['odometer']['value'],
            'hv_percentage': data['fuelLevel'],
            'hv_range': data['distanceToEmpty']['value'],
            'ev_percentage': data['batteryLevel'],
            'timestamp': data['timestamp'],
            'charging_status': data['chargingStatus'],
        }
        return telemetry, fresh

    def get_remote_control_status(self):
        """
        Get location information. Location is saved when vehicle is powered off. Save data to
        CACHE_DIR/remote_control/remote_control-`datetime` file.
        :return: Location dict, fresh Boolean if new data was fetched
        """
        fresh = False
        remote_control_path = Path(CACHE_DIR) / 'remote_control'
        remote_control_file = remote_control_path / 'remote_control-{}'.format(pendulum.now())
        url = f'{MYT_API_URL}/v1/global/remote/electric/status'
        r = requests.get(url, headers=self.headers)
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
        OBSOLETE!

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
    # OBSOLETE!
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


def ev_data_to_db(myt, fresh, data):
    if fresh and myt.config_data['use_influxdb']:
        log.debug('Saving EV data to influxdb')
        insert_into_influxdb('charge_level', data['batteryLevel'])
        insert_into_influxdb('ev_range', data['evRangeWithAc']['value'])
        insert_into_influxdb('hv_level', data['fuelLevel'])
        insert_into_influxdb('hv_range', data['fuelRange']['value'])


def odometer_to_db(myt, fresh, fuel_percent, odometer):
    if fresh and myt.config_data['use_influxdb']:
        log.debug('Saving odometer data to influxdb')
        insert_into_influxdb('odometer', odometer)
        insert_into_influxdb('fuel_level', fuel_percent)


def trip_data_to_db(myt, fresh, average_consumption, kms, liters):
    if fresh and myt.config_data['use_influxdb']:
        insert_into_influxdb('trip_kilometers', kms)
        insert_into_influxdb('trip_liters', liters)
        insert_into_influxdb('trip_average_consumption', average_consumption)


def print_trip_stats(trip):
    duration = trip['summary']['duration']
    length = trip['summary']['length']

    try:
        ev_time = trip['hdc']['evTime'] / duration * 100
    except KeyError:
        ev_time = 0
    try:
        eco_time = trip['hdc']['ecoTime'] / duration * 100
    except KeyError:
        eco_time = 0
    try:
        power_time = trip['hdc']['powerTime'] / duration * 100
    except KeyError:
        power_time = 0
    try:
        charge_time = trip['hdc']['chargeTime'] / duration * 100
    except KeyError:
        charge_time = 0
    try:
        ev_dist = trip['hdc']['evDistance'] / length * 100
    except KeyError:
        ev_dist = 0
    try:
        eco_dist = trip['hdc']['ecoDist'] / length * 100
    except KeyError:
        eco_dist = 0
    try:
        power_dist = trip['hdc']['powerDist'] / length * 100
    except KeyError:
        power_dist = 0
    try:
        charge_dist = trip['hdc']['chargeDist'] / length * 100
    except KeyError:
        charge_dist = 0
    print('Time stats:       EV: {:.0f}%\teco: {:.0f}%\tpower: {:.0f}%\tcharging: {:.0f}%'.
          format(ev_time, eco_time, power_time, charge_time))
    print('Distance stats:   EV: {:.0f}%\teco: {:.0f}%\tpower: {:.0f}%\tcharging: {:.0f}%'.
          format(ev_dist, eco_dist, power_dist, charge_dist))


def main():
    """
    Get parking information, get odometer information, get remote control information, get trips information
    :return:
    """
    myt = Myt()

    log.info('Get parking info...')
    parking, fresh = myt.get_parking()
    try:
        latitude = parking['payload']['vehicleLocation']['latitude']
        longitude = parking['payload']['vehicleLocation']['longitude']
        parking_date = pendulum.parse(parking['payload']['lastTimestamp']).in_tz(myt.config_data['timezone']).to_datetime_string()
        print('Car was parked at {} {} at {}'.format(latitude, longitude, parking_date))
    except KeyError:
        print('Failed to get parking data')

    # Get odometer and fuel tank status
    log.info('Get odometer info...')
    try:
        telemetry, fresh = myt.get_telemetry()
        print('Odometer {} km, {}% fuel left'.format(telemetry['odometer'], telemetry['hv_percentage']))
        print('EV {}%, status: {} at {}'.format(telemetry['ev_percentage'], telemetry['charging_status'],
                                                pendulum.parse(telemetry['timestamp']).in_tz(myt.config_data['timezone']).to_datetime_string()))
        odometer_to_db(myt, fresh, telemetry['hv_percentage'], telemetry['odometer'])
    except ValueError:
        print('Didn\'t get odometer information!')

    # Get remote control status
    if myt.config_data['use_remote_control']:
        log.info('Get remote control status...')
        status, fresh = myt.get_remote_control_status()

        data = status['payload']
        print('Battery level {}%, EV range {} km, Fuel level {}%, HV range {} km, Charging status {}, status reported at {}'.
              format(data['batteryLevel'], data['evRangeWithAc']['value'],
                     data['fuelLevel'], data['fuelRange']['value'],
                     data['chargingStatus'],
                     pendulum.parse(data['lastUpdateTimestamp']).
                     in_tz(myt.config_data['timezone']).to_datetime_string()
                     ))
        if data['chargingStatus'] == 'charging' and data['remainingChargeTime'] != 65535:
            acquisition_datetime = pendulum.parse(data['lastUpdateTimestamp'])
            charging_end_time = acquisition_datetime.add(minutes=data['remainingChargeTime'])
            print('Charging will be completed at {}'.format(charging_end_time.in_tz(myt.config_data['timezone']).
                                                            to_datetime_string()))
        if data['chargingStatus'] == 'charging' and data['remainingChargeTime'] == 65535:
            print('Pulling power from the plug but not really charging')
        ev_data_to_db(myt, fresh, data)
        # remote_control_to_db(myt, fresh, charge_info, hvac_info)

    log.info('Get trips...')
    trips, fresh = myt.get_trips()
    # Get detailed information about trips and calculate cumulative kilometers and fuel liters
    kms = 0
    ls = 0
    fresh_data = 0
    for trip in trips['payload']['trips']:
        trip_data, fresh = myt.get_trip(trips['payload']['trips'], trip['id'])
        fresh_data += fresh
        # Parse UTC datetime strings to local time
        start_time = pendulum.parse(trip['summary']['startTs']).in_tz(myt.config_data['timezone']).to_datetime_string()
        end_time = pendulum.parse(trip['summary']['endTs']).in_tz(myt.config_data['timezone']).to_datetime_string()
        start_address = f'{trip["summary"]["startLat"]} {trip["summary"]["startLon"]}'
        end_address = f'{trip["summary"]["endLat"]} {trip["summary"]["endLon"]}'
        length = trip['summary']['length']/1000
        liters = trip['summary']['fuelConsumption']/1000
        kms += length
        ls += liters
        average_consumption = (liters/length)*100
        trip_data_to_db(myt, fresh, average_consumption, kms, liters)
        print('{} {} -> {} {}: {} km, {} km/h, {:.2f} l/100 km, {:.2f} l'.
              format(start_time, start_address, end_time, end_address, length,
                     trip['summary']['averageSpeed'], average_consumption, liters))
        print_trip_stats(trip)

    if fresh_data and myt.config_data['use_influxdb']:
        insert_into_influxdb('short_term_average_consumption', (ls/kms)*100)
    print('Total distance: {:.3f} km, Fuel consumption: {:.2f} l, {:.2f} l/100 km'.format(kms, ls, (ls/kms)*100))


if __name__ == "__main__":
    sys.exit(main())
