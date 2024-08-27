import tensorflow as tf
import numpy as np
import os
from load_model import main as load_model

def get_model_weights(model):
    return {var.name: var.numpy() for var in model.variables}

def average_weights(weight_list):
    avg_weights = {}
    for var_name in weight_list[0].keys():
        avg_weights[var_name] = np.mean([weights[var_name] for weights in weight_list], axis=0)
    return avg_weights

def set_model_weights(model, weights):
    for var in model.variables:
        if var.name in weights:
            var.assign(weights[var.name])

def average_models(model_names, versions):
    models = []
    for name, version in zip(model_names, versions):
        model = load_model(name, version)
        models.append(model)

    weight_list = [get_model_weights(model) for model in models]
    avg_weights = average_weights(weight_list)

    averaged_model = models[0]
    set_model_weights(averaged_model, avg_weights)

    return averaged_model

def print_model_weights(model):
    print(f"\033[92mAveraged model weights:\033[0m ({len(model.variables)} variables)")
    for var in model.variables:
        print(f"{var.name}: {var.shape}")