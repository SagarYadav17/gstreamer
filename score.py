import asyncio
import websockets
import json
from flask import render_template, Flask, render_template_string
import subprocess
from datetime import datetime, timedelta

from time import sleep
from datetime import datetime, timedelta


app = Flask(__name__)


# async def stream():

#     # # Connect to the WebSocket and continuously receive messages
#     # async with websockets.connect("ws://3.110.33.117/ws/chat/") as ws:
#     #     while True:
#     #         message = await ws.recv()
#     #         message = json.loads(message).get("message", default_message)

#     #         print(message)
#     #         # Pass the message into an HTML template
#     #         with app.app_context():
#     #             generate_image(message)

#     generate_image(default_message)


# asyncio.run(stream())

default_message = {
    "team_a": "Team A",
    "team_b": "Team B",
    "team_a_score": 0,
    "team_b_score": 0,
    "time": "00:00",
}

# Convert the time string to a datetime object
time_obj = datetime.strptime(default_message["time"], "%H:%M")

options = [
    "--quality",
    "100",
    "--width",
    "1920",
    "--height",
    "1080",
    "--transparent",
]


def generate_image(message: dict):
    with app.app_context():
        html_template = render_template("score.html", **message)
        subprocess.run(
            ["wkhtmltoimage"] + options + ["-", "image.png"],
            input=html_template.encode(),
        )


while True:
    html_data = generate_image(default_message)

    # Add 1 minute to the time
    time_obj += timedelta(minutes=1)

    # Convert the datetime object back to a string
    time = time_obj.strftime("%H:%M")
    default_message["time"] = time

    sleep(1)
