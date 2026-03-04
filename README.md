<img src="resources/images/qfoam-logo-v1.png" alt="Quantum Foam Spot VPNs" width="200">

# Quantum Foam Spot VPNs

Quantum Foam is a CLI tool that lets you quickly provision on-demand, ephemeral VPN instances across multiple cloud providers. Every component of the instance, including SSH keys, is completely temporary. This is ideal for ad-hoc secure connections—such as accessing region-restricted services—without leaving behind persistent infrastructure.

## Virtual Environment Setup

    python3 -m venv qfoam
    source qfoam/bin/activate
    pip install -r requirements.txt

## CLI Usage

    python3 qfoam-cli.py create --provider <provider> --region <region> --size <size> --image <image>
    python3 qfoam-cli.py list
    python3 qfoam-cli.py delete --provider <provider> --region <region> --suffix <suffix>

> <small>Note: The first run will create a vpn.db file in the same directory as the cli. This keeps track of the VPNs that are created.</small>

## Docker

    docker build -t qfoam .
    docker run -it --rm qfoam create --provider <provider> --region <region> --size <size> --image <image>
    docker run -it --rm qfoam list
    docker run -it --rm qfoam delete --provider <provider> --region <region> --suffix <suffix>

## Cloud Providers

### _DigitalOcean_

#### Setup
To use DigitalOcean, you will need to set the following environment variables:

    DIGITALOCEAN_TOKEN
To communicate with the DigitalOcean API.
See [DigitalOcean Personal Access Token](https://docs.digitalocean.com/reference/api/create-personal-access-token/) to learn how to create a token.

#### Pricing
DigitalOcean droplets give you a specific amount of egress bandwidth for free - based on the droplet size. After that amount of bandwidth is used up, they charge per GB of egress bandwidth. See [DigitalOcean Droplet Pricing](https://www.digitalocean.com/pricing/droplets) under Transfer.

### _GCP_ (Coming soon)

#### Setup
You will need to install the [Google Cloud CLI](https://cloud.google.com/sdk/docs/install) to use GCP as a provider.
