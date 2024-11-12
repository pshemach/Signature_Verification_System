from flask import Flask, jsonify, request
from sigVrfy.utils.general import is_allowed
from sigVrfy.pipelines.process_images import compare_signatures
import logging
from werkzeug.exceptions import HTTPException

app = Flask(__name__)

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)


@app.errorhandler(Exception)
def handle_exception(e):
    """Handle uncaught exceptions and HTTP errors."""
    if isinstance(e, HTTPException):
        return jsonify({"error": e.description}), e.code
    else:
        app.logger.error(f"Unexpected error: {e}")
        return (
            jsonify({"error": "An unexpected error occurred. Please try again later."}),
            500,
        )


@app.route("/predict", methods=["POST"])
def predict():
    try:
        if request.method != "POST":
            return jsonify({"error": "Invalid request method. Use POST."}), 405

        img_1 = request.files.get("image1")
        img_2 = request.files.get("image2")

        if not img_1 or not img_2:
            app.logger.warning("One or both images are missing.")
            return jsonify({"error": "Both image1 and image2 are required."}), 400

        if not (is_allowed(img_1.filename) and is_allowed(img_2.filename)):
            app.logger.warning("Invalid image format detected.")
            return (
                jsonify(
                    {
                        "error": "Invalid image format. Allowed file types: jpg, jpeg, png."
                    }
                ),
                415,
            )

        try:
            prediction = compare_signatures([img_1, img_2])
        except Exception as e:
            app.logger.error(f"Error in signature comparison: {e}")
            return (
                jsonify(
                    {"error": "Failed to process images. Please check your input."}
                ),
                500,
            )

        return jsonify({"prediction": prediction})

    except Exception as e:
        app.logger.error(f"Error in /predict endpoint: {e}")
        return (
            jsonify({"error": "An unexpected error occurred. Please try again later."}),
            500,
        )


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5056, debug=True)
