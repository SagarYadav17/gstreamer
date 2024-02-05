import gi
import logging


gi.require_version("Gst", "1.0")
from gi.repository import Gst, GLib

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)


def update_overlay_location(pipeline, overlay):
    on_timeout(pipeline)

    # Get the current position in the pipeline
    success, position = pipeline.query_position(Gst.Format.TIME)
    if not success:
        logging.info("Failed to get the position, using the default image.")
        # use the default image
        image_file_path = f"images/image_000000.png"
    else:
        # Convert position from nanoseconds to seconds
        position_seconds = position // Gst.SECOND
        image_file_path = f"images/image_{position_seconds:06}.png"

    # Update the image file path
    overlay.set_property("location", image_file_path)

    return True  # Continue calling this function


def start_pipeline(video_file_path: str, output_file_path: str) -> None:
    Gst.init(None)

    pipeline_string = (
        f"filesrc location={video_file_path} ! decodebin name=dec "
        f"dec. ! queue ! videoconvert ! gdkpixbufoverlay name=overlay location=images/image_000000.png ! x264enc ! queue ! mp4mux name=mux ! filesink location={output_file_path} "
        f"dec. ! queue ! audioconvert ! audioresample ! voaacenc ! queue ! mux. "
    )
    pipeline = Gst.parse_launch(pipeline_string)

    # Get the overlay element
    overlay = pipeline.get_by_name("overlay")

    # Set up bus to receive messages
    bus = pipeline.get_bus()
    bus.add_signal_watch()
    bus.connect("message", on_bus_message, GLib.MainLoop.new(None, False))

    # Start the pipeline
    pipeline.set_state(Gst.State.PLAYING)

    # Run the main loop
    loop = GLib.MainLoop()

    # Add a timeout callback to update the overlay location every second
    GLib.timeout_add(100, update_overlay_location, pipeline, overlay)

    loop.run()
    loop.quit()
    exit("Done")


def on_timeout(pipeline):
    position_query = Gst.Query.new_position(Gst.Format.TIME)
    duration_query = Gst.Query.new_duration(Gst.Format.TIME)

    if pipeline.query(position_query) and pipeline.query(duration_query):
        position = position_query.parse_position()[1] / Gst.SECOND
        duration = duration_query.parse_duration()[1] / Gst.SECOND
        logging.debug(f"Position: {position}s / {duration}s")

    # Return True to keep the timeout
    return True


def on_bus_message(bus, message, loop):
    t = message.type
    if t == Gst.MessageType.EOS:
        logging.debug("End of stream")
        loop.quit()
        exit("Done")
    elif t == Gst.MessageType.ERROR:
        err, debug_info = message.parse_error()
        logging.error(f"Error: {err} - {debug_info}")
        loop.quit()
        exit("Error")
