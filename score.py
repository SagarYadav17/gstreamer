import imgkit
import asyncio
import websockets
import json
from flask import render_template, Flask
import cv2
import numpy as np


app = Flask(__name__)


def generate_image(message: dict):
    with app.app_context():
        html_template = render_template("score.html", **message)
        # Render the HTML to an image
        imgkit.from_string(html_template, "image.png")

        # Load the image`
        image = cv2.imread("image.png")

        # Convert the image to RGBA
        image_rgba = cv2.cvtColor(image, cv2.COLOR_BGR2BGRA)

        # Define the color range for pure white
        lower = np.array([254, 254, 254], dtype=np.uint8)
        upper = np.array([255, 255, 255], dtype=np.uint8)

        # Create a mask that only includes the pure white pixels
        mask = cv2.inRange(image, lower, upper)

        # Set the alpha channel to 0 for the white pixels and 255 for the other pixels
        image_rgba[:, :, 3] = np.where(mask == 255, 0, 255)

        # Save the result
        cv2.imwrite("image.png", image_rgba)


async def stream():
    default_message = {
        "team_a": "Team A",
        "team_b": "Team B",
        "team_a_score": 0,
        "team_b_score": 0,
    }

    # Connect to the WebSocket and continuously receive messages
    async with websockets.connect("ws://3.110.33.117/ws/chat/") as ws:
        while True:
            message = await ws.recv()
            message = json.loads(message).get("message", default_message)

            print(message)
            # Pass the message into an HTML template
            with app.app_context():
                generate_image(message)


asyncio.run(stream())
