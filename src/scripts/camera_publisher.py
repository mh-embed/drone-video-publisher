import cv2
import gi
import picamera
import picamera.array
import numpy as np

gi.require_version("Gst", "1.0")
gi.require_version("GstRtspServer", "1.0")
from gi.repository import Gst, GstRtspServer


class SensorFactory(GstRtspServer.RTSPMediaFactory):
    def __init__(self, **properties):
        super(SensorFactory, self).__init__(**properties)
        self.cap = cv2.VideoCapture(self.get_launch())

    def get_launch(self):
        return (
            "appsrc ! videoconvert ! x264enc tune=zerolatency speed-preset=superfast ! rtph264pay pt=96 name=pay0 "
        )

    def create_element(self, url):
        return self.cap

    def need_data(self, src, length):
        ret, frame = self.cap.read()
        if not ret:
            return

        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        frame_data = frame.tostring()

        buf = Gst.Buffer.new_allocate(None, len(frame_data), None)
        buf.fill(0, frame_data)
        buf.pts = buf.dts = int(self.num_frames * (1 / 30.0) * Gst.SECOND)
        self.duration = buf.duration = int((1 / 30.0) * Gst.SECOND)
        self.num_frames += 1

        src.emit("push-buffer", buf)

    def do_create_element(self):
        src = Gst.ElementFactory.make("appsrc", "source")
        src.set_property("caps", Gst.Caps.from_string("video/x-raw,format=RGB,width=640,height=480,framerate=30/1"))

        src.connect("need-data", self.need_data)
        return src


def main(args):
    # Initialize camera
    with picamera.PiCamera() as camera:
        with picamera.array.PiRGBArray(camera) as stream:
            camera.resolution = (640, 480)
            camera.framerate = 30

            # Initialize GStreamer and RTSP server
            Gst.init(None)

            server = GstRtspServer.RTSPServer.new()
            server.set_service("8554")
            mounts = server.get_mount_points()
            factory = SensorFactory()
            mounts.add_factory("/test", factory)
            server.attach(None)

            print("RTSP server is running at rtsp://<your_raspberry_pi_ip_address>:8554/test")
            print("Press Ctrl+C to stop the server")

            # Run the server and camera capture loop
            try:
                while True:
                    camera.capture(stream, format="bgr", use_video_port=True)
                    factory.cap.write(np.asarray(stream.array))
                    stream.truncate(0)

            except KeyboardInterrupt:
                print("Stopping server...")
                server = None
                Gst.deinit()

if __name__ == "__main__":
    import sys
    sys.exit(main(sys.argv))