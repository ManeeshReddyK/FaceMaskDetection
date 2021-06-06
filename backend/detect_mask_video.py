from tensorflow.keras.applications.mobilenet_v2 import preprocess_input
from tensorflow.keras.preprocessing.image import img_to_array
from flask import Flask, Response, request, send_file
from tensorflow.keras.models import load_model
from imutils.video import VideoStream
from PIL import Image as pimg
from flask_cors import CORS
import numpy as np
import imutils
import cv2
import io

app = Flask(__name__)
cors = CORS(app)

data = {}
data['vs'] = None

prototxtPath = r"model\deploy.prototxt"
weightsPath = r"model\res10_300x300_ssd_iter_140000.caffemodel"
faceNet = cv2.dnn.readNet(prototxtPath, weightsPath)
maskNet = load_model("mask_detector.model")


def get_prediction(frame):
    (locs, preds) = detect_and_predict_mask(frame, faceNet, maskNet)
    for (box, pred) in zip(locs, preds):
        (startX, startY, endX, endY) = box
        (mask, withoutMask) = pred
        label = "Mask" if mask > withoutMask else "No Mask"
        color = (0, 255, 0) if label == "Mask" else (0, 0, 255)
        cv2.putText(frame, label, (startX, startY - 10),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.45, color, 2)
        cv2.rectangle(frame, (startX, startY), (endX, endY), color, 2)
    return frame


def detect_and_predict_mask(frame, faceNet, maskNet):

    (h, w) = frame.shape[:2]
    blob = cv2.dnn.blobFromImage(frame, 1.0, (224, 224), (104.0, 177.0, 123.0))

    faceNet.setInput(blob)
    detections = faceNet.forward()

    faces = []
    locs = []
    preds = []

    for i in range(0, detections.shape[2]):
        confidence = detections[0, 0, i, 2]
        if confidence > 0.5:
            box = detections[0, 0, i, 3:7] * np.array([w, h, w, h])
            (startX, startY, endX, endY) = box.astype("int")
            (startX, startY) = (max(0, startX), max(0, startY))
            (endX, endY) = (min(w - 1, endX), min(h - 1, endY))

            face = frame[startY:endY, startX:endX]
            face = cv2.cvtColor(face, cv2.COLOR_BGR2RGB)
            face = cv2.resize(face, (224, 224))
            face = img_to_array(face)
            face = preprocess_input(face)

            faces.append(face)
            locs.append((startX, startY, endX, endY))

    if len(faces) > 0:
        faces = np.array(faces, dtype="float32")
        preds = maskNet.predict(faces, batch_size=32)

    return (locs, preds)


def gen_frames():
    data['vs'] = VideoStream(src=0).start()
    while True:
        frame = data['vs'].read()
        frame = imutils.resize(frame, width=400)
        frame = get_prediction(frame)
        ret, buffer = cv2.imencode('.jpg', frame)
        frame = buffer.tobytes()
        yield (b'--frame\r\n'b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')


def predict_mask_an_image(image):
    pillow_img = pimg.open(io.BytesIO(image))
    pillow_img.save("request"+'.jpg')
    image = cv2.imread('request.jpg')
    frame = imutils.resize(image, width=400)
    return get_prediction(frame)


@app.route('/video_feed')
def video_feed():
    return Response(gen_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')


@app.route('/video_release')
def video_release():
    data['vs'].stream.release()
    return Response('End')


@app.route('/image_feed', methods=['POST'])
def face_mask_detection():
    file = request.files['Image'].read()
    tagged_image = predict_mask_an_image(file)
    cv2.imwrite("response.png", tagged_image)
    pillow_img = pimg.open("response.png")
    img_io = io.BytesIO()
    pillow_img.save(img_io, 'JPEG')
    img_io.seek(0)
    return send_file(img_io, mimetype='image/jpeg')


if __name__ == '__main__':
    app.run(debug=True)
