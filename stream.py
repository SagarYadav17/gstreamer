import gi
import logging

gi.require_version("Gst", "1.0")
from gi.repository import Gst, GLib

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


def start_pipeline(restream_url: str, stream_url: str) -> None:
    Gst.init(None)

    # GStreamer pipeline for HLS restreaming
    pipeline_string = (
        f"uridecodebin uri={stream_url} name=dec "
        f"dec. ! queue ! videoconvert ! mix.sink_0 "
        f"dec. ! queue ! audioconvert ! autoaudiosink "
        f'multifilesrc location=image.png caps="image/png,framerate=(fraction)1/1" loop=true ! '
        f"pngdec ! videoconvert ! gdkpixbufoverlay offset-x=0 offset-y=0 ! mix.sink_1 "
        f"videomixer name=mix ! videoconvert ! autovideosink"
    )

    # pipeline_string = (
    #     f"uridecodebin uri={stream_url} name=dec "
    #     f"dec. ! queue ! videoconvert ! mix.sink_0 "
    #     f"dec. ! queue ! audioconvert ! audioresample ! voaacenc ! queue ! flvmux. "
    #     f'multifilesrc location=image.png caps="image/png,framerate=(fraction)1/1" loop=true ! '
    #     f"pngdec ! videoconvert ! gdkpixbufoverlay offset-x=0 offset-y=0 ! mix.sink_1 "
    #     f"videomixer name=mix ! videoconvert ! x264enc tune=zerolatency ! flvmux name=flvmux ! queue ! rtmpsink location={restream_url}"
    # )

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


# Example usage
restream_url = ""
stream_url = ""

start_pipeline(restream_url, stream_url)
