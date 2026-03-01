# Quantum Foam Spot VPNs

Quantum Foam is a CLI tool that lets you quickly provision on-demand, ephemeral VPN instances across multiple cloud providers. Every component of the instance, including SSH keys, is completely temporary. This is ideal for ad-hoc secure connections—such as accessing region-restricted services—without leaving behind persistent infrastructure.

## Virtual Environment Setup

    python3 -m venv qfoam
    source qfoam/bin/activate
    pip install -r requirements.txt

## CLI Usage

    python3 qfoam-cli.py create
    python3 qfoam-cli.py list
    python3 qfoam-cli.py delete <suffix>

## Environment variables

    DIGITALOCEAN_TOKEN
    TAILSCALE_AUTH_KEY

    export DIGITALOCEAN_TOKEN="your_digitalocean_token"
    export TAILSCALE_AUTH_KEY="your_tailscale_auth_key"

## Docker

    docker build -t qfoam .
    docker run -it --rm qfoam create
    docker run -it --rm qfoam list
    docker run -it --rm qfoam delete <suffix>

## Pricing by Cloud

### DigitalOcean
DigitalOcean droplets give you a specific amount of egress bandwidth for free - based on the droplet size. After that amount of bandwidth is used up, they charge per GB of egress bandwidth. See [DigitalOcean Droplet Pricing](https://www.digitalocean.com/pricing/droplets) under Transfer.

### GCP