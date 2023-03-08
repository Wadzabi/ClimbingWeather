import pymongo
import dash
from dash import dcc, html, Dash
from datetime import datetime, timedelta
from dotenv import dotenv_values
import certifi
import plotly.express as px
from pandas import json_normalize
import pandas as pd


ca = certifi.where()


config = dotenv_values(".env")


client = pymongo.MongoClient(config["MONGODB_CONNECTION"], tlsCAFile=ca)
db = client["ClimbingWeather"]
collection = db["weatherdata"]


def serve_layout():
# Retrieve data from the last 24 hours
    time_threshold = datetime.utcnow() - timedelta(days=10)
    df = json_normalize(list(collection.find({"datetime": {"$gte": time_threshold}})))



    fig1 = px.line(df, x="datetime", y=["sensor.temperature", "openweather.temperature"], labels={"datetime": "Time", "value": "Temperature (°C) ", "variable": "Source"}, markers=True)
    fig2 = px.line(df, x="datetime", y=["sensor.humidity", "openweather.humidity"], labels={"datetime": "Time", "value": "Relative humidity (%)", "variable": "Source"}, markers=True)

    fig1.update_layout(
        xaxis=dict(
            autorange=True,
            range=[df["datetime"].min(), df["datetime"].max()],
            rangeslider=dict(
                autorange=True,
                range=[df["datetime"].min(), df["datetime"].max()]
            ),
            type="date"
        )
    )

    fig2.update_layout(
        xaxis=dict(
            autorange=True,
            range=[df["datetime"].min(), df["datetime"].max()],
            rangeslider=dict(
                autorange=True,
                range=[df["datetime"].min(), df["datetime"].max()]
            ),
            type="date"
        )
    )

    return html.Div(children=[
        html.H1(children='Weatherdata for climbers'),

        dcc.Markdown('''
        ### A demo page for a climbers school project

        Comparing weatherdata from OpenWeatherMap and a LoRaWAN temperature and humidity sensor placed at a climbing location. Updates once every hour.\n
        Current location is Orminge. Find potential problems to climb on [27Crags](https://27crags.com/crags/orminge)

        '''),
        html.H3("Last update was " + str(int((datetime.utcnow() - df["datetime"].max()).total_seconds()//60)) + " minutes ago."),

        dcc.Graph(
            id='temp_graph',
            figure=fig1
        ),
        dcc.Graph(
            id='humidity_graph',
            figure=fig2
        )
    ])


app = Dash(__name__)

app.layout = serve_layout

if __name__ == '__main__':
    app.run_server(debug=True)



