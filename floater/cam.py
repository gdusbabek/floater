import os
from picamera import PiCamera
import time

PHOTO_DIR = os.path.join(os.environ.get('MEDIA_HOME', '/home/pi/Pictures'), 'photos')
VIDEO_DIR = os.path.join(os.environ.get('MEDIA_HOME', '/home/pi/Pictures'), 'videos')

cam = PiCamera()

def next_photo_path():
    idx = 0
    while True:
        photo_path = os.path.join(PHOTO_DIR, f"capture_{idx:04d}.jpg")
        if os.path.exists(photo_path):
            idx += 1
        else:
            return photo_path

def next_video_path():
    idx = 0
    while True:
        video_path = os.path.join(VIDEO_DIR, f"capture_{idx:04d}.h264")
        if os.path.exists(video_path):
            idx += 1
        else:
            return video_path

def capture_photo():
    photo_path = next_photo_path()
    cam.start_preview()
    time.sleep(4)
    cam.capture(photo_path)
    cam.stop_preview()
    return photo_path

def capture_video(seconds=30):
    video_path = next_video_path()
    cam.start_recording(video_path)
    cam.wait_recording(seconds)
    cam.stop_recording()
    return video_path
