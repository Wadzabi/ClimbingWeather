import paho.mqtt.client as mqtt
import json
import requests
from datetime import datetime
from dotenv import dotenv_values
import pymongo
import certifi

ca = certifi.where()

temperature_measurement_Id = 4097
humidity_measurement_Id = 4098

config = dotenv_values(".env")


client = pymongo.MongoClient(config["MONGODB_CONNECTION"], tlsCAFile=ca)
db = client["ClimbingWeather"]
collection = db["weatherdata"]


def get_sensor_data(sensor_messages):
    temperature, humidity = None, None
    for message in sensor_messages:
        if message["measurementId"] == temperature_measurement_Id:
            temperature = message["measurementValue"]
        elif message["measurementId"] == humidity_measurement_Id:
            humidity = message["measurementValue"]
    return format_weatherdata(temperature, humidity)

#Get weatherdara from openweathermap api
def get_openweather_data(lat, lon):
    api_endpoint = "https://api.openweathermap.org/data/2.5/weather"
    params = {
        "lat": lat,
        "lon": lon,
        "appid": config["OPENWEATHER_KEY"],
        "units": "metric"
    }

    weather_data = requests.get(api_endpoint, params=params).json()

    return format_weatherdata(weather_data["main"]["temp"], weather_data["main"]["humidity"])

#SMHI and YRNO to be implemented
def get_smhi_data(lat, lon):
    return format_weatherdata(-2, 50)

def get_yrno_data(lat, lon):
    return format_weatherdata(-3, 50)



def format_weatherdata(temperature, humidity):
    return {"temperature": temperature, "humidity": humidity}


def payload_handler(sensor_payload):
    sensor_data = sensor_payload["uplink_message"]["decoded_payload"]["messages"]
    sensor_lat = sensor_payload["uplink_message"]["locations"]["user"]["latitude"]
    sensor_lon = sensor_payload["uplink_message"]["locations"]["user"]["longitude"]

    db_item = {
        "datetime": datetime.utcnow(),
        "location": {
            "lat": sensor_lat,
            "lon": sensor_lon
        },
        "sensor": get_sensor_data(sensor_data),
        "openweather": get_openweather_data(sensor_lat, sensor_lon)
    }

    print(db_item)


    collection.insert_one(db_item)

# MQTT event functions
def on_connect(mqttc, obj, flags, rc):
    print("\nConnect: rc = " + str(rc))

def on_message(mqttc, obj, msg):
    print("\nMessage: " + msg.topic + " " + str(msg.qos)) 
    sensor_payload = json.loads(msg.payload)
    payload_handler(sensor_payload)

def on_subscribe(mqttc, obj, mid, granted_qos):
    print("\nSubscribe: " + str(mid) + " " + str(granted_qos))


#Setup mqtt client and connect securley with tls to TTN Server.
mqttc = mqtt.Client()

mqttc.on_connect = on_connect
mqttc.on_subscribe = on_subscribe
mqttc.on_message = on_message



mqttc.username_pw_set(config["MQTT_USERNAME"], config["MQTT_PASSWORD"])

mqttc.tls_set(ca)	

mqttc.connect(config["MQTT_SERVER"], 8883, 60)

mqttc.subscribe("v3/+/devices/+/up", 0)	# all device uplinks

mqttc.loop_forever()
