import torch
from sigVrfy.utils.normalize_image import preprocess_signature
from sigVrfy.utils.general import load_config, load_signature
from sigVrfy.models.signet import SigNet
from sigVrfy.constant import CONFIG_PATH, CANVAS_SIZE

config = load_config(config_path=CONFIG_PATH)

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

model = None


def load_model():
    global model
    if model is None:
        state_dict, _, _ = torch.load(config["model"]["segmentation_path"])
        model = SigNet().to(device).eval()
        model.load_state_dict(state_dict)


def compare_signatures(images_path, canvas_size=CANVAS_SIZE):
    load_model()
    user_signs = [load_signature(path) for path in images_path]
    processed_user_sigs = torch.tensor(
        [preprocess_signature(sig, canvas_size) for sig in user_signs]
    )
    processed_user_sigs_scaled = (
        processed_user_sigs.view(-1, 1, 150, 220).float().div(255)
    )
    with torch.no_grad():
        user_features = model(processed_user_sigs_scaled.to(device))

    distance = torch.norm(user_features[0] - user_features[1])
    print(f"Euclidean distance between signatures from the same user: {distance}")

    if distance < 15.5:
        return "Original"
    else:
        return "Forged"
