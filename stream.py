restream_url = ""  # noqa
stream_url = "https://cdn.flowplayer.com/a30bd6bc-f98b-47bc-abf5-97633d4faea0/hls/de3f6ca7-2db3-4689-8160-0f574a5996ad/playlist.m3u8"

import gi  # noqa
import logging  # noqa
import os

# os.environ["GST_DEBUG"] = "6"

gi.require_version("Gst", "1.0")
from gi.repository import Gst, GLib  # noqa

# Set up logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)


def on_bus_message(bus, message, loop):
    t = message.type
    if t == Gst.MessageType.EOS:
        logger.debug("End of stream")
        loop.quit()
    elif t == Gst.MessageType.ERROR:
        err, debug_info = message.parse_error()
        logger.error(f"Error: {err} - {debug_info}")
        loop.quit()
    return True


Gst.init(None)

# GStreamer pipeline for HLS restreaming
pipeline_string = (
    f"videomixer name=mix sink_0::zorder=0 sink_1::zorder=1 ! "
    f"videoconvert ! x264enc ! queue leaky=downstream max-size-buffers=0 max-size-bytes=0 max-size-time=0 ! "
    f"flvmux name=mux ! rtmpsink location={restream_url} "
    f"uridecodebin uri={stream_url} name=dec "
    f"dec. ! queue leaky=downstream max-size-buffers=0 max-size-bytes=0 max-size-time=0 ! videoconvert ! mix. "
    f"dec. ! queue leaky=downstream max-size-buffers=0 max-size-bytes=0 max-size-time=0 ! audioconvert ! voaacenc ! queue leaky=downstream max-size-buffers=0 max-size-bytes=0 max-size-time=0 ! mux. "
    f'multifilesrc location=image.png caps="image/png,framerate=(fraction)1/1" ! '
    f"pngdec ! videoconvert ! mix."
)

pipeline = Gst.parse_launch(pipeline_string)


# Set up bus to receive messages
bus = pipeline.get_bus()
bus.add_signal_watch()
bus.connect("message", on_bus_message, GLib.MainLoop.new(None, False))


# Start the pipeline
logger.debug("Starting the pipeline")
pipeline.set_state(Gst.State.PLAYING)

# Run the main loop
logger.debug("Running the main loop")
loop = GLib.MainLoop()
loop.run()
loop.quit()
