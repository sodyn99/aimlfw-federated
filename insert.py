import influxdb_client
from influxdb_client.client.write_api import SYNCHRONOUS
import numpy as np
from datetime import datetime
from rich.progress import Progress
from rich.console import Console
from rich.table import Table
from rich.progress import track

console = Console()

def connect_influxdb(url, token, org, bucket):
    client = influxdb_client.InfluxDBClient(
        url=url,
        token=token,
        org=org
    )
    write_api = client.write_api(write_options=SYNCHRONOUS)
    return client, write_api

def insert_model_weights(write_api, bucket, org, model, model_name, version):
    weights_data = []

    total_variables = sum([var.numpy().flatten().size for var in model.variables])  # Total number of weights

    with Progress() as progress:
        task = progress.add_task(f"[cyan]Inserting weights for {model_name} (version {version})...", total=total_variables)

        for var in model.variables:
            var_name = var.name.replace(':', '_')
            flat_weights = var.numpy().flatten().tolist()
            weights_data.extend(flat_weights)
            for i, weight in enumerate(flat_weights):
                point = influxdb_client.Point("model_weights") \
                    .tag("model", model_name) \
                    .tag("version", version) \
                    .tag("layer", var_name) \
                    .tag("index", str(i)) \
                    .field("weight", float(weight)) \
                    .time(datetime.utcnow())
                write_api.write(bucket=bucket, org=org, record=point)

                progress.advance(task, 1)

    table = Table(title=f"Weights Summary for {model_name} (version {version})")
    table.add_column("Statistic", justify="right", style="cyan", no_wrap=True)
    table.add_column("Value", style="magenta")

    table.add_row("Total Weights", str(len(weights_data)))
    table.add_row("Mean", f"{np.mean(weights_data):.4f}")
    table.add_row("Std Dev", f"{np.std(weights_data):.4f}")
    table.add_row("Min", f"{np.min(weights_data):.4f}")
    table.add_row("Max", f"{np.max(weights_data):.4f}")

    console.print(table)
    console.print(f"Weights of model {model_name} (version {version}) have been saved to InfluxDB.")

def main(model, model_name, version, url, token, org, bucket):
    client, write_api = connect_influxdb(url, token, org, bucket)
    insert_model_weights(write_api, bucket, org, model, model_name, version)
    client.close()
