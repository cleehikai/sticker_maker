from flask import Flask, render_template, request, send_file
from PIL import Image
import os
import io

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

def remove_white_background(img, threshold=240):
    """
    Converts white-ish background to transparent in an RGBA image.
    """
    img = img.convert("RGBA")
    datas = img.getdata()

    newData = []
    for item in datas:
        if item[0] > threshold and item[1] > threshold and item[2] > threshold:
            # Make pixel transparent
            newData.append((255, 255, 255, 0))
        else:
            newData.append(item)

    img.putdata(newData)
    return img

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        border_thickness = int(request.form.get('border', 50))
        file = request.files['image']

        if file:
            img = Image.open(file)

            # Convert to RGBA and remove white background if JPEG or not transparent
            if img.mode != "RGBA":
                img = img.convert("RGBA")
                img = remove_white_background(img)

            # Create a new image with black background
            new_width = img.width + 2 * border_thickness
            new_height = img.height + 2 * border_thickness
            background = Image.new("RGBA", (new_width, new_height), (0, 0, 0, 255))
            background.paste(img, (border_thickness, border_thickness), mask=img)

            img_io = io.BytesIO()
            background.save(img_io, 'PNG')
            img_io.seek(0)

            return send_file(img_io, mimetype='image/png', as_attachment=True, download_name='sticker.png')

    return render_template('index.html')

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)