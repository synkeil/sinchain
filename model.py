import datetime

from flask import Flask, render_template

import numpy as np
import tensorflow as tf
from tensorflow import keras
from keras.utils.np_utils import to_categorical

from PIL import Image
import os
from os import path
from flask import request, jsonify, make_response
import io

num_classes = 0


# Chargement du jeu de données :
def load_signaux(dir):
    img_list = []
    class_counter = 0
    class_list = []
    for i in os.listdir(dir):
        if (path.isdir(path.join(dir, i))):
            for j in os.listdir(path.join(dir, i)):
                if (j.endswith('.ppm')):
                    class_list.append(class_counter)
                    img_list.append(np.array(Image.open(os.path.join(os.path.join(dir, i), j)).resize((28, 28))))
            class_counter += 1
    return np.array(img_list), np.array(class_list)

# define the function to pre-process the 
def transform_image(image_bytes):
  image_file = io.BytesIO(image_bytes)
  

  return image_file

def open_ppm_img(img):
    test_predict = Image.open(img).resize((28, 28))
    test_predict = np.array(test_predict).astype("float32")/255.0
    test_predict = test_predict.reshape(1, 28, 28, 3)

    return test_predict

def predict(to_predict, model):
    prediction = model.predict(to_predict)
    proba_array = prediction.argsort()
    best_guess = proba_array[0][-1]
    return best_guess

def data(a,b):
  print (a,b)
  return (a,b)

app = Flask(__name__)

@app.route('/')
def root():
    # For the sake of example, use static information to inflate the template.
    # This will be replaced with real information in later steps.
    dummy_times = [datetime.datetime(2018, 1, 1, 10, 0, 0),
                   datetime.datetime(2018, 1, 2, 10, 30, 0),
                   datetime.datetime(2018, 1, 3, 11, 0, 0),
                   ]

    (X_test, y_test) = load_signaux("static/Test")

    y_test = to_categorical(y_test)
    num_classes = y_test.shape[1]

    model = keras.models.load_model("static/model")

    test_loss, test_accuracy = model.evaluate(X_test, y_test)

    predictions = model.predict(X_test)

    return render_template('index.html', times=dummy_times, results=[test_loss, test_accuracy], check=data(test_loss, test_accuracy)
    )



@app.route("/forward/", methods=['POST'])
def move_forward():
    # get file from web
    data = request.files['file']

    data.save(data.filename)

    #preproc de l'image
    themage = open_ppm_img(data.filename)
    
    model = keras.models.load_model("static/model")

    print ("VALUE",predict(themage, model))

    return render_template('index.html')

if __name__ == '__main__':
    # This is used when running locally only. When deploying to Google App
    # Engine, a webserver process such as Gunicorn will serve the app. This
    # can be configured by adding an `entrypoint` to app.yaml.
    # Flask's development server will automatically serve static files in
    # the "static" directory. See:
    # http://flask.pocoo.org/docs/1.0/quickstart/#static-files. Once deployed,
    # App Engine itself will serve those files as configured in app.yaml.
    app.run(host='127.0.0.1', port=8080, debug=True)