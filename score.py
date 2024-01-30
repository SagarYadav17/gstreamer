import asyncio
import websockets
import json
import subprocess
import requests
import os
import logging
from datetime import datetime, timedelta
import dotenv

from flask import render_template, Flask


# Set up
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)
dotenv.load_dotenv()


app = Flask(__name__)

email = os.environ.get("EMAIL")
password = os.environ.get("PASSWORD")

if not email or not password:
    raise Exception("EMAIL and PASSWORD environment variables are required")

login_url = "https://gs360.balizado.sagaryadav.dev/api/iam/login/"
body = {
    "email": email,
    "password": password,
}

default_message = {
    "team_a": "Team A",
    "team_b": "Team B",
    "team_a_score": 0,
    "team_b_score": 0,
    "time": "00:00",
}

wkhtmltoimage_options = [
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
            ["wkhtmltoimage"] + wkhtmltoimage_options + ["-", "image.png"],
            input=html_template.encode(),
        )


def auth():
    response = requests.post(login_url, data=body)

    if response.status_code == 200:
        return response.json().get("access")

    return None


async def run_score(livestream_id: str):
    token = auth()
    # Convert the time string to a datetime object
    time_obj = datetime.strptime(default_message["time"], "%H:%M")

    async with websockets.connect(
        f"wss://gs360.balizado.sagaryadav.dev/ws/live-updates/{livestream_id}/?token={token}"
    ) as ws:
        while True:
            message = await ws.recv()
            message = json.loads(message).get("data", {})

            score_data = message.get("message", default_message)
            status = message.get("status")

            # if status in ["finished", "discarded"]:
            #     exit("Stream has ended")

            while True:
                time_obj += timedelta(minutes=1)
                time = time_obj.strftime("%H:%M")
                score_data["time"] = time
                generate_image(score_data)
                await asyncio.sleep(1)
