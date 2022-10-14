from ambient_api.ambientapi import AmbientAPI

import sys
import time
import random
import yaml
from azure.iot.hub import IoTHubRegistryManager
from azure.iot.hub.models import Twin, TwinProperties, QuerySpecification, QueryResult

import json

device_data_exmaple = \
    [
        {
            "macAddress": "00:00:00:00:00:00",
            "info": {
                "name": "My Weather Station",
                "location": "Home"
            },
            "lastData": {
                "dateutc": 1515436500000,
                "date": "2018-01-08T18:35:00.000Z",
                "winddir": 58,
                "windspeedmph": 0.9,
                "windgustmph": 4,
                "maxdailygust": 5,
                "windgustdir": 61,
                "winddir_avg2m": 63,
                "windspdmph_avg2m": 0.9,
                "winddir_avg10m": 58,
                "windspdmph_avg10m": 0.9,
                "tempf": 66.9,
                "humidity": 30,
                "baromrelin": 30.05,
                "baromabsin": 28.71,
                "tempinf": 74.1,
                "humidityin": 30,
                "hourlyrainin": 0,
                "dailyrainin": 0,
                "monthlyrainin": 0,
                "yearlyrainin": 0,
                "feelsLike": 66.9,
                "dewPoint": 34.45380707462477
            }
        }
    ]


def send_to_azure(data: dict, config: dict) -> None:
    try:
        iot_reg_manager = IoTHubRegistryManager(config.get('IOTHUB_CONNECTION_STRING'))

        #make a tag for Device twin
        last_data = {'Weather_Station_Data': data}

        twin = iot_reg_manager.get_twin(config.get('DEVICE_ID'))
        twin_patch = Twin(tags=last_data, properties=TwinProperties(desired={'power_level': 1}))
        twin = iot_reg_manager.update_twin(config.get('DEVICE_ID'), twin_patch, twin.etag)

        #send every 3 seconds
        time.sleep(3)
    except Exception as ex:
        print("Unexpected error {0}".format(ex))
        return
    except KeyboardInterrupt:
        print("Keyboard interrupt detected stopping detection!")

    return None


def main():
    with open("config/weather_station_config.yaml") as config_file:
        config = yaml.load(config_file, Loader=yaml.FullLoader)
    # First we would set up an Ambient Weather account with the device. 
    #
    config = dict(config)
    print(config)
    api = AmbientAPI()
    api.api_key = config.get('API_KEY')
    api.application_key = config.get('APP_KEY')
    devices = api.get_devices()
    #
    # #could add some try except blocks here if it doesn't work.
    device = devices[0]
    # weather_data = json.loads(device.getData())[n] <-- n is the first and only device we have so it would be 0
    #
    # print(device.getData()) <-- This would be device_data_example lies
    f = open('datafile.txt', "w")
    while True:
        #   ideally this would be weather_data = json.loads(device.getData())["lastData"] 
        #   if we had an account set up with MAC address.
        data = device.get_data(limit=config.get('DAYS_LIMIT'))
        if len(data) == 0:
            continue
        print(data, file=f)
        print(data)
        print("\n", file=f)
        time.sleep(3)
        send_to_azure(data, config)

    return None


if __name__ == "__main__":
    main()
