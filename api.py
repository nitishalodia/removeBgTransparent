from rembg import remove
from PIL import Image
import os
from flask import Flask, request, redirect, url_for, render_template, send_from_directory, jsonify, send_file

from werkzeug.utils import secure_filename
import cloudinary

import sys
#
#
# cloudinary.config(
#     cloud_name = "db5g1vegd",
#     api_key = "381722484831413",
#     api_secret = "iDkNvcjW8RXBSJNIuoWf5YMiKv0",
#     secure = true
# )
import cloudinary.uploader
import cloudinary.api


UPLOAD_FOLDER = os.path.dirname(os.path.abspath(__file__))
ALLOWED_EXTENSIONS = {'jpg', 'jpeg','png','JPG','JPEG','PNG'}

app = Flask(__name__,static_url_path="/static")
DIR_PATH = os.path.dirname(os.path.realpath(__file__))
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# limit upload size upto 8mb
app.config['MAX_CONTENT_LENGTH'] = 8 * 1024 * 1024

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route('/getmsg/', methods=['GET'])
def respond():
    # Retrieve the name from the url parameter /getmsg/?name=
    name = request.args.get("name", None)

    # For debugging
    print(f"Received: {name}")

    response = {}

    # Check if the user sent a name at all
    if not name:
        response["ERROR"] = "No name found. Please send a name."
    # Check if the user entered a number
    elif str(name).isdigit():
        response["ERROR"] = "The name can't be numeric. Please send a string."
    else:
        response["MESSAGE"] = f"Welcome {name} to our awesome API!"

    # Return the response in json format
    return jsonify(response)


@app.route('/removeBg/', methods=['GET'])
def removeBg():
    # Retrieve the name from the url parameter /getmsg/?name=
    input_path = request.args.get("inputImage", None)

    output_path = 'car-removedPython2.png'

    input = Image.open(input_path)
    output = remove(input)
    output.save(output_path)

    # For debugging
    print(f"Received: {input_path}")
    response = {}
    # Return the response in json format
    return jsonify(response)


@app.route('/post/', methods=['POST'])
def post_something():
    param = request.form.get('name')
    print(param)
    # You can add the test cases you made in the previous function, but in our case here you are just testing the POST functionality
    if param:
        return jsonify({
            "Message": f"Welcome {name} to our awesome API!",
            # Add this option to distinct the POST request
            "METHOD": "POST"
        })
    else:
        return jsonify({
            "ERROR": "No name found. Please send a name."
        })


#@app.route('/')
#def index():
   # A welcome message to test our server
#    return "<h1>Welcome to our medium-greeting-api!</h1>"


@app.route('/download')
def downloadFile ():
    #For windows you need to use drive name [ex: F:/Example.pdf]
    path1 =os.path.join(app.config['UPLOAD_FOLDER'],'car-removed.png')
    print("FINAL DOWNLOAD PATH  "  + path1)
    return send_file(path1, as_attachment=True)


@app.route('/uploads/<path:filename>', methods=['GET', 'POST'])
def download(filename):
    # Appending app path to upload folder path within app root folder
    path1 =os.path.join(app.config['UPLOAD_FOLDER'],filename)
    print("FINAL DOWNLOAD PATH  "  + path1)
    return send_file(path1, as_attachment=True)
    # uploads = os.path.join(current_app.root_path, app.config['UPLOAD_FOLDER'])
    # # Returning file from appended path
    # return send_from_directory(directory=uploads, filename=filename)

@app.route("/",methods=['GET', 'POST'])
def index():
    upload_result = None
    output_path = ''
    output_image = ''
    path1 = ''

    if request.method == 'POST':
        if 'file' not in request.files:
            print('No file attached in request')
            return redirect(request.url)
        file = request.files['file']
        if file.filename == '':
            print('No file selected')
            return redirect(request.url)
        if file and allowed_file(file.filename):
            print('IN UPLOADED FILES')
            upload_result = None
            output_path = ''
            output_image = ''
            path1 = ''
            filename = secure_filename(file.filename)

            file.save(os.path.join(app.config['UPLOAD_FOLDER'],filename))
            input_path = filename
            # output_image = filename.replace('.png', '') + "-removed.png"
            output_image = "cleaned-image.png"

            input = Image.open(input_path)
            output = remove(input)
            path1 =os.path.join(app.config['UPLOAD_FOLDER'],output_image)
            print("changed path  " + path1 )
            output.save(path1)
            print(filename)
            upload_result = True


        path =(os.path.join(app.config['UPLOAD_FOLDER'],filename))
        print("path :",path)
        result = path.split("/")
        filename2 = result[-1:]
        filename1 = " ".join(filename2)

    return render_template('index.html',
                           upload_result= upload_result,
                           output_image = output_image)

if __name__ == '__main__':
    # Threaded option to enable multiple instances for multiple user access support
    app.run(threaded=True, port=5000)
