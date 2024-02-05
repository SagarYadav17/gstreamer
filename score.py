import asyncio
import subprocess
import logging
from datetime import timedelta

from flask import render_template, Flask
from datetime import datetime


# Set up
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)


app = Flask(__name__)
START_DATETIME = datetime(2019, 1, 1, 0, 0, 0)

default_message = {
    "team_a": "Team A",
    "team_b": "Team B",
    "team_a_score": 0,
    "team_b_score": 0,
    "time": "00:00:00",
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


def generate_image(message: dict, image_name: str = "image.png") -> None:
    with app.app_context():
        html_template = render_template("score.html", **message)
        subprocess.run(
            ["wkhtmltoimage"] + wkhtmltoimage_options + ["-", image_name],
            input=html_template.encode(),
        )


async def run_score() -> None:
    score_data = default_message

    time_obj = START_DATETIME

    for i in range(70):
        time_obj = (START_DATETIME + timedelta(seconds=i)).time()

        score_data["time"] = time_obj.strftime("%H:%M:%S")
        image_name = f"./images/image_{time_obj.strftime('%H%M%S')}.png"

        generate_image(score_data, image_name)
        print(score_data["time"])


if __name__ == "__main__":
    asyncio.run(run_score())
