from average_models import average_models, print_model_weights
from insert import main as insert_to_influxdb
import yaml

def load_config(config_path):
    with open(config_path, 'r') as file:
        config = yaml.safe_load(file)
    return config

config = load_config('/app/config.yaml')

#---------------------------------------------------
#----- Load Configurations from config.yaml --------
#---------------------------------------------------

url = config['influxdb']['url']
token = config['influxdb']['token']
org = config['influxdb']['org']
bucket = config['influxdb']['bucket']

model_names = config['models']['names']
versions = config['models']['versions']

gobal_model_name = config['global_model']['name']
global_model_version = config['global_model']['version']

#---------------------------------------------------

averaged_model = average_models(model_names, versions)
print_model_weights(averaged_model)

insert_to_influxdb(averaged_model, "global_model", "1", url, token, org, bucket)