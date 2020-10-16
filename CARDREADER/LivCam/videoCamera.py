import cv2
import tensorflow as tf
import pytesseract
from PIL import Image
import numpy as np
import json
from django.http import JsonResponse
from django.http import HttpResponse
import pathlib
pytesseract.pytesseract.tesseract_cmd = 'C:\\Program Files\\Tesseract-OCR\\tesseract.exe'
path_to_classifier = pathlib.Path("../model/classifier2.h5").resolve()
image_container = "none"
last_text = "No card detected <br><br><br><br><br> Please Hold the card steadily for few seconds while aligned to the white guide on the camera view to the left <br><br><br><br> This screen will automatically populate with the detected text <br><br><br><br>"
last_key = {"status":"No-Key-detected"}

class VideoCamera(object):
    def __init__(self):
        self.video = cv2.VideoCapture(0)
    
    def __del__(self):
        self.video.release()
    
    def get_frame(self):
        global image_container
        success, image = self.video.read()
        print("video-ok")
        image_container = image
        ret, jpeg = cv2.imencode('.jpg', image)
        return jpeg

def detectcard(card):
    tmep = "holder"
    global last_text
    global last_key
    if type(image_container) == type(tmep):
        return JsonResponse({'last_text': last_text, "last_key": last_key, "first": "1"})
    else:
        print("=======================Request handelled======================")
        gray = cv2.cvtColor(card, cv2.COLOR_BGR2GRAY)
        valid = model.predict(np.expand_dims(np.expand_dims(gray, 2),0))
        if valid >= 0.5:
            print("|||||||||||||||||||||||||||||TEXT DETECTED|||||||||||||||||||||||||||||||||")
            last_text, last_key = extract_text(card)
            return JsonResponse({'last_text': last_text, "last_key": last_key, "first": "0"})
        else:
            return JsonResponse({'last_text': last_text, "last_key": last_key, "first": "1"})

def extract_text(card):
    cam_pic_size = (1280, 720)
    print(type(card), card.shape)
    frame = cv2.resize(card, dsize=cam_pic_size, interpolation=cv2.INTER_CUBIC)
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    adaptive_threshold = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 85, 8)
    text = pytesseract.image_to_string(adaptive_threshold, lang = "eng+hin")
    key_values = extract_key(text)
    print(str(text))
    return str(text), key_values


def extract_key(sample, extract = None):
    if extract == None:
        extract = {
            'gujarat state': (1, 'ba', None),
            'maharashtra state': (1, 'ba', None),
            'driving licence': (1, 'ba', None),
            'name': (2, None, None),
            'address': (3, None, None),
            'dob': (1, 'bg', None),
            'bg': (1, None, None),
            'जन्म तारीख': (1, None, "dob"),
            'पुरुष': (1, None, "gender"),
            'special': (3, 's', 'name')
        }
    lines = sample.split("\n")
    flines = [l for l in lines if len(l) > 5]
    track = []
    for i, line in enumerate(flines):
        for key in extract:
            result = line.lower().find(key)
            if result != -1: track.append({
                "key": key,
                "index": result,
                "position": i
            })
    this = {}
    for t in track:
        count = extract[t['key']][0]
        val = extract[t['key']][1]
        alt = extract[t['key']][2]

        if val == 'ba':
            this[t['key']] = flines[t['position']][t["index"]:t["index"]+len(t['key'])]
        elif val == None:
            put = flines[t['position']][t["index"]+len(t['key']):]
            put = put + " ".join(flines[t['position']+1: t['position']+count])
            if alt:
                this[alt] = put
            else:
                this[t['key']] = put
        else:
            here = flines[t['position']].lower().find(val)
            put = flines[t['position']][t["index"]+len(t['key']):here]
            this[t['key']] = put
    this["potential interest"] = [x for x in flines if len(x.split()) == 3]
    return this

def gen(camera):
    global model 
    model = tf.keras.models.load_model(path_to_classifier)
    while True:
        frame = camera.get_frame()
        frame = frame.tobytes()
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n\r\n')

def get_image():
    return image_container