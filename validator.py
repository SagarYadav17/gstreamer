import uuid
import argparse


def validate_uuid(value):
    try:
        uuid.UUID(value)
    except ValueError:
        raise argparse.ArgumentTypeError("Invalid livestream ID")
    return value


def validate_dash_url(value):
    if not value.startswith("https://") or not value.endswith(".mpd"):
        raise argparse.ArgumentTypeError("Invalid Dash URL")
    return value
