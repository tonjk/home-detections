import os
import yaml

config_path = os.path.join(os.path.dirname(__file__), "model_config.ymal")
with open(config_path, "r") as f:
    config = yaml.safe_load(f)

MODEL_NAME = config['models']['name']
MODEL_CONF = config['models']['conf']
MODEL_CLASSES = config['models']['classes']

NOTI_FRAME_THRESHOLD = config['noti']['frame_threshold']
NOTI_COOLDOWN = config['noti']['noti_cooldown']