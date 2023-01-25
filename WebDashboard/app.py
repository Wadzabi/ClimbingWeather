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

# Retrieve data from the last 24 hours
time_threshold = datetime.utcnow() - timedelta(hours=24)
df = json_normalize(list(collection.find({"datetime": {"$gte": time_threshold}})))

fig = px.line(df, x="datetime", y=["sensor.temperature", "openweather.temperature"])

app = Dash(__name__)

app.layout = html.Div(children=[
    html.H1(children='Hello Dash'),

    html.Div(children='''
        Dash: A web application framework for your data.
    '''),

    dcc.Graph(
        id='example-graph',
        figure=fig
    )
])

if __name__ == '__main__':
    app.run_server(debug=True)



