import os
import subprocess
import logging
import tensorflow as tf
import shutil

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def run_command(command):
    result = subprocess.run(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    if result.returncode != 0:
        error_message = f"\033[91mCommand execution failed: {result.stderr.decode()}\033[0m"
        logger.error(error_message)
        print(error_message)
        return False, result.stderr.decode()
    else:
        logger.info(f"Command output: {result.stdout.decode()}")
        return True, result.stdout.decode()

def download_and_extract_model(trainingjob_name, version):
    url = f"http://tm.traininghost:32002/model/{trainingjob_name}/{version}/Model.zip"
    base_output_dir = "/models"
    custom_folder_name = f"{trainingjob_name}_{version}"  # trainingjobName_version
    output_dir = os.path.join(base_output_dir, custom_folder_name)  # /models/trainingjobName_version
    zip_path = os.path.join(output_dir, "Model.zip")  # /models/trainingjobName_version/Model.zip
    temp_dir = "/tmp/model_temp"

    os.makedirs(output_dir, exist_ok=True)

    download_command = f"curl -o {zip_path} {url}"
    logger.info(f"Downloading model from {url}")
    success, output = run_command(download_command)
    if not success:
        logger.error("Model download failed.")
        return None

    logger.info(f"Model successfully downloaded to {zip_path}.")

    unzip_command = f"unzip -o {zip_path} -d {temp_dir}"
    logger.info(f"Unzipping model to {temp_dir}")
    success, output = run_command(unzip_command)
    if not success:
        logger.error("Model extraction failed.")
        return None

    inner_dir = os.path.join(temp_dir, "1")
    if os.path.exists(inner_dir):
        for item in os.listdir(inner_dir):
            s = os.path.join(inner_dir, item)
            d = os.path.join(output_dir, item)
            if os.path.isdir(s):
                shutil.copytree(s, d, dirs_exist_ok=True)
            else:
                shutil.copy2(s, d)
    else:
        logger.warning(f"Expected directory structure not found: {inner_dir}")
        for item in os.listdir(temp_dir):
            s = os.path.join(temp_dir, item)
            d = os.path.join(output_dir, item)
            if os.path.isdir(s):
                shutil.copytree(s, d, dirs_exist_ok=True)
            else:
                shutil.copy2(s, d)

    shutil.rmtree(temp_dir)
    os.remove(zip_path)
    logger.info("Model files moved and temporary files deleted.")

    return output_dir

def load_model(model_path):
    logger.info(f"Loading model from {model_path}")
    try:
        model = tf.saved_model.load(model_path)
        logger.info("Model successfully loaded in SavedModel format")
        return model
    except Exception as e:
        logger.warning(f"Failed to load in SavedModel format: {str(e)}")
        logger.info("Attempting to load as a Keras model...")
        try:
            model = tf.keras.models.load_model(model_path)
            logger.info("Model successfully loaded in Keras model format")
            return model
        except Exception as e2:
            logger.error(f"Failed to load model: {str(e2)}")
            return None

def main(trainingjob_name, version):
    model_dir = download_and_extract_model(trainingjob_name, version)
    if model_dir:
        return load_model(model_dir)
    else:
        logger.error("Failed to download and extract model")
        return None