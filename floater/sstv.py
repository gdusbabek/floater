import subprocess
import os
import logging

PYTHONHOME = os.environ.get('PYTHONHOME', '/home/pi/tracker_env/bin')

def annotate_img(img_src, img_dest, info):
    """
    convert /Users/gdusbabek/Desktop/test_photos/capture_0139.jpg -fill '#0008' -draw 'rectangle 65,5,5,30' -fill white -annotate +10+20 KI5GRD /Users/gdusbabek/Desktop/test_photos/capture_0139_ano.jpg
    convert /Users/gdusbabek/Desktop/test_photos/capture_0139.jpg -background Black -fill white label:'KI5GRD' -gravity Center -append /Users/gdusbabek/Desktop/test_photos/capture_0139_ano.jpg
    """
    # params = ['convert', img_src, '-fill', shlex.quote('#0008'), '-draw', shlex.quote('rectangle 65,5,5,30'), '-fill', 'white', '-annotate', '+10+141', callsign, img_dest]
    params = ['convert', img_src, '-pointsize', '16', '-background', 'Black', '-fill', 'white', f"label:{info}", '-gravity', 'Center', '-append', img_dest]
    try:
        res = subprocess.check_output(params, shell=False)
        return img_dest
    except subprocess.CalledProcessError as ex:
        return None

def img_to_wav(img_path, wav_path):
    """
    pi images default to 1280 × 720.
    This does Martin M1, 16 bits per sample at 48k.
    """
    try:
        subprocess.check_output([os.path.join(PYTHONHOME, 'python'), '-m', 'pysstv', '--resize', img_path, wav_path])
        return True
    except subprocess.CalledProcessError as ex:
        logging.error(ex.output)
        return False
