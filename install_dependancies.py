import subprocess

def run_command(command):
    process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    while True:
        output = process.stdout.readline()
        if process.poll() is not None and output == b'':
            break
        if output:
            print(output.decode().strip())

    rc = process.poll()
    return rc

run_command("pip install rich")

from rich.console import Console
from rich.live import Live
from rich.panel import Panel
from time import sleep

console = Console()

dependencies = [
    "pyyaml",
    "influxdb_client",
    "flask",
    "tensorflow==2.15.0"
]

with Live(console=console, refresh_per_second=4) as live:
    for dep in dependencies:
        panel = Panel(f"Installing {dep}", title="Dependency Installation")
        live.update(panel)
        run_command(f"pip install {dep}")
        sleep(1)

console.print("All dependencies installed successfully!")