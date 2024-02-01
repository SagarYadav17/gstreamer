import asyncio
import websockets
import json
import logging
import dotenv
import docker

from score import auth


# Set up
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)
dotenv.load_dotenv()
client = docker.from_env()


def get_active_container_names() -> list[str]:
    return [item.name for item in client.containers.list(all=True)]


def create_container(live_stream_id: str, stream_url: str, restream_url: str):
    env_vars = {
        "LIVESTREAM_ID": live_stream_id,
        "STREAM_URL": stream_url,
        "RESTREAM_URL": restream_url,
        "EMAIL": "",
        "PASSWORD": "",
    }

    cpu_quota = int(60 * 100000)  # 60% of the system (in microseconds)

    client.containers.run(
        image="gstreamer:latest",
        name=live_stream_id,
        cpu_period=100000,  # Set the CPU period (in microseconds)
        cpu_quota=cpu_quota,  # Set the CPU quota (in microseconds)
        detach=True,
        environment=env_vars,
        remove=True,
    )


async def get_livestreams():
    token = auth()
    # Convert the time string to a datetime object

    async with websockets.connect(
        f"wss://dev-gs360.balizado.sagaryadav.dev/ws/active-live-streams/?token={token}"
    ) as ws:
        while True:
            message = await ws.recv()
            message = json.loads(message).get("data", {})

            running_container_names = get_active_container_names()

            for stream in message:
                stream_id = stream.get("id")
                stream_url = stream.get("camera_details", {}).get("dash")
                restream_url = stream.get("camera_details", {}).get("restream_url")
                if stream_id not in running_container_names:
                    create_container(stream_id, stream_url, restream_url)


async def main():
    await get_livestreams()


if __name__ == "__main__":
    asyncio.run(main())
