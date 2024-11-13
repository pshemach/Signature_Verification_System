import os
from flask import Flask, render_template, request, jsonify
from sigVrfy.utils.general import is_allowed, make_dir
from sigVrfy.pipelines.process_images import compare_signatures
from sigVrfy.constant import UPLOAD_FOLDER
from werkzeug.utils import secure_filename


app = Flask(__name__)
app.config["UPLOAD_FOLDER"] = "static/uploads"
os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/predict", methods=["POST"])
def predict():
    if request.method == "POST":
        img_1 = request.files.get("image1")
        img_2 = request.files.get("image2")

        if not img_1 or not img_2:
            return jsonify({"error": "Both image1 and image2 are required."}), 400

        if not (is_allowed(img_1.filename) and is_allowed(img_2.filename)):
            return (
                jsonify(
                    {
                        "error": "Invalid image format. Allowed file types: jpg, jpeg, png."
                    }
                ),
                415,
            )

        # Save images for processing
        img_1_path = os.path.join(
            app.config["UPLOAD_FOLDER"], secure_filename(img_1.filename)
        )
        img_2_path = os.path.join(
            app.config["UPLOAD_FOLDER"], secure_filename(img_2.filename)
        )
        img_1.save(img_1_path)
        img_2.save(img_2_path)

        # Process images and get prediction
        try:
            prediction = compare_signatures([img_1, img_2])
        except Exception as e:
            return jsonify({"error": "Failed to process images."}), 500

        # Prepare the response data
        response_data = {
            "prediction": prediction,
            "image1_url": img_1_path,
            "image2_url": img_2_path,
        }

        # Delete the images after processing
        try:
            os.remove(img_1_path)
            os.remove(img_2_path)
        except Exception as e:
            app.logger.error(f"Error deleting images: {e}")

        return jsonify(response_data)


if __name__ == "__main__":
    make_dir(UPLOAD_FOLDER)
    app.run(host="0.0.0.0", port="5057", debug=True)
