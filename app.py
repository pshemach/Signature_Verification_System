from flask import Flask, jsonify, request
from sigVrfy.utils.general import is_allowed

app = Flask(__name__)


@app.route("/predict", methods=["POST"])
def predict():
    if request.method == "POST":
        img_1 = request.files.get("image1")
        img_2 = request.files.get("image2")
        if (
            img_1
            and img_2
            and is_allowed(img_1.filename)
            and is_allowed(img_2.filename)
        ):
            # Process the images and make predictions
            prediction = make_prediction(img_1, img_2)
            return jsonify({"prediction": prediction})
        else:
            return (
                jsonify(
                    {
                        "error": "Invalid image format.  Allowed file types: jpg, jpeg, png."
                    }
                ),
                415,
            )

    return jsonify({"error": "Invalid request method. Use POST."}), 405
