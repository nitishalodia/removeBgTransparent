from rembg import remove
from PIL import Image
import os
from flask import Flask, request, redirect, url_for, render_template, send_from_directory, jsonify, send_file
from werkzeug.utils import secure_filename
import sys
import warnings
import cv2
import numpy as np
import cloudinary
from cloudinary.uploader import upload
import cloudinary.api
from cloudinary.utils import cloudinary_url
from waitress import serve



UPLOAD_FOLDER = os.path.dirname(os.path.abspath(__file__))
ALLOWED_EXTENSIONS = {'jpg', 'jpeg','png','JPG','JPEG','PNG'}

app = Flask(__name__,static_url_path="/static")
DIR_PATH = os.path.dirname(os.path.realpath(__file__))
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# limit upload size upto 8mb
app.config['MAX_CONTENT_LENGTH'] = 8 * 1024 * 1024

cloudinary.config(
    cloud_name = "db5g1vegd",
    api_key = "381722484831413",
    api_secret = "iDkNvcjW8RXBSJNIuoWf5YMiKv0",
    secure = True
)
#https://381722484831413:iDkNvcjW8RXBSJNIuoWf5YMiKv0@api.cloudinary.com/v1_1/db5g1vegd/ping





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


@app.route('/bgRemove/', methods=['GET'])
def removeBg():
    # Retrieve the name from the url parameter /getmsg/?name=
    input_path = request.args.get("inputImage", None)
    output_path = 'car-removedPython2.png'

    input = Image.open(input_path)
    output = remove(input)
    output.save(output_path)
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

# def brighten(filename):
#     img_bgr: np.ndarray = cv2.imread(filename, cv2.IMREAD_COLOR)
#     x_bgr: torch.Tensor = K.utils.image_to_tensor(img_bgr)
#     x_rgb: torch.Tensor = K.color.bgr_to_rgb(x_bgr)
#     x_rgb = x_rgb.float() / 255.0
#
#     # adjust brightness
#     # x_out: torch.Tensor = K.enhance.adjust_brightness(x_rgb, torch.linspace(0.2, 0.8, 4))
#     x_out: torch.Tensor = K.enhance.adjust_brightness(
#         x_rgb, .4)
#     out_np: np.ndarray = K.utils.tensor_to_image(x_out)
#     im = Image.fromarray((out_np * 255).astype(np.uint8))
#     out_img = filename.replace('.png', '') + "-bright.png"
#     im.save(out_img)
#     return out_img

    # # x_out is torch.Tensor, converting that to image
    # out: torch.Tensor = torchvision.utils.make_grid(x_out, nrow=2, padding=5)
    # out_np: np.ndarray = K.utils.tensor_to_image(out)
    #
    # im = Image.fromarray((out_np * 255).astype(np.uint8))
    #
    # im.save("your_file.jpeg")

@app.route("/removeBg",methods=['GET', 'POST'])
def process_image():
    upload_result = None
    output_image_name = ''
    removedbg_path = ''
    img_brighten = ''
    filename = ''
    img_url = ''
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
        filename = secure_filename(file.filename) #input image filename
        file.save(os.path.join(app.config['UPLOAD_FOLDER'],filename))

        img_url = upload_cloudinary(filename)

        input_path = filename
        output_image_name = filename.replace('.png', '') + "-removed.png"
        # output_image_name = "cleaned-image.png"
        print("FILENAME   "+ os.path.join(app.config['UPLOAD_FOLDER'],filename))
        img_removedBg = removeBackground(input_path)

        removedbg_path =os.path.join(app.config['UPLOAD_FOLDER'],output_image_name)
        print("changed path  " + removedbg_path )
        img_removedBg.save(removedbg_path)     #output image filename


        outPut_rembg_image_url = upload_cloudinary(output_image_name)
        print(filename)
        os.remove(os.path.join(app.config['UPLOAD_FOLDER'],filename))
        os.remove(os.path.join(app.config['UPLOAD_FOLDER'],removedbg_path))
        upload_result = True

        print(upload_result.to)
    return jsonify({'msg': 'success', 'input_url': img_url ,'output_url': outPut_rembg_image_url})


@app.route("/",methods=['GET', 'POST'])
def index():
    # upload_result = None
    # output_image = ''
    # removedbg_path = ''
    # img_brighten = ''
    # filename = ''
    # img_url = ''
    #
    # if request.method == 'POST':
    #     if 'file' not in request.files:
    #         print('No file attached in request')
    #         return redirect(request.url)
    #     file = request.files['file']
    #     if file.filename == '':
    #         print('No file selected')
    #         return redirect(request.url)
    #     if file and allowed_file(file.filename):
    #         print('IN UPLOADED FILES')
    #         upload_result = None
    #         output_image = ''
    #         removedbg_path = ''
    #         img_brighten = ''
    #         img_url = ''
    #
    #         filename = secure_filename(file.filename)
    #         file.save(os.path.join(app.config['UPLOAD_FOLDER'],filename))
    #
    #         img_url = upload_cloudinary(filename)
    #
    #         input_path = filename
    #         output_image = filename.replace('.png', '') + "-removed.png"
    #         # output_image = "cleaned-image.png"
    #         print("FILENAME   "+ os.path.join(app.config['UPLOAD_FOLDER'],filename))
    #         img_removedBg = removeBackground(input_path)
    #
    #         removedbg_path =os.path.join(app.config['UPLOAD_FOLDER'],output_image)
    #         print("changed path  " + removedbg_path )
    #         img_removedBg.save(removedbg_path)
    #         print(filename)
    #         upload_result = True
    #
    #         bright_img = brighten(filename)
    #         img_brighten = upload_cloudinary(bright_img)
    #
    #
    #     path =(os.path.join(app.config['UPLOAD_FOLDER'],filename))
    #     print("path :",path)
    #     result = path.split("/")
    #     filename2 = result[-1:]
    #     filename1 = " ".join(filename2)

    # return render_template('index.html',
    #                        filename = img_url,
    #                        upload_result= upload_result,
    #                        output_image = output_image,
    #                        bright_image = img_brighten)
    response = "Welcome to background removal api"
    return jsonify(response)


def removeBackground(filename):
    image = Image.open(filename)
    img_removedBg = remove(image)
    return img_removedBg

def upload_cloudinary(filename):
    response = upload(filename, tags='image upload')
    img_url, options = cloudinary_url(
        response['public_id'],
        format=response['format'],
        width=200,
        height=150,
        crop="fill"
    )
    return img_url

if __name__ == '__main__':
    # Threaded option to enable multiple instances for multiple user access support
    app.run(threaded=True, port=8000)
    #serve(app, host='0.0.0.0', port=80)
