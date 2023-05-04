import base64
import pandas as pd
from io import BytesIO
from pathlib import Path

from flask import Flask, render_template, request
from PIL import Image, ImageSequence

app = Flask(__name__)
IMAGE_DIR = Path("static/img")
CSV_FILE = Path("db.csv")


def create_gif(image_path):
    """Converts the image at `image_path` to a GIF file."""
    with Image.open(image_path) as im:
        gif_bytes = BytesIO()
        # Loop over each frame of the image and add it to the GIF file
        for frame in ImageSequence.Iterator(im):
            gif_bytes.seek(0)
            frame.save(gif_bytes, format="gif")
            gif_bytes.seek(0)
        return gif_bytes.getvalue()


def find_image_filenames(input_text):
    """Returns a list of image filenames for the given input text."""
    df = pd.read_csv(CSV_FILE)
    filtered_rows = df[df["kelas"].isin(input_text.split())]
    return filtered_rows["location"].tolist()


@app.route("/", methods=["GET", "POST"])
def index():
    gif = None
    if request.method == "POST":
        # Get the user input from the form data
        input_text = request.form.get("input_text")
        # Find the image filenames for the input text
        image_filenames = find_image_filenames(input_text)
        if not image_filenames:
            # If no image filenames are found, return an error message
            return render_template("index.html", error="No image found for input")
        # Create a GIF file from the image files and pass it to the view
        image_paths = [IMAGE_DIR / filename for filename in image_filenames]
        gif_bytes = BytesIO()
        with Image.open(image_paths[0]) as im:
            im.save(gif_bytes, format="gif", save_all=True, append_images=[
                    Image.open(p) for p in image_paths[1:]], duration=2000, loop=100)
        gif = base64.b64encode(gif_bytes.getvalue()).decode()
        # Pass the base64-encoded string to the view
        return render_template("index.html", gif=gif, input_text=input_text)
    else:
        return render_template("index.html")
