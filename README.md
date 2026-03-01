# Spot VPNs

This tool allows you to create, list, and delete spot VPN instances on DigitalOcean and connect them to a Tailscale. Everything within the VPN instance is ephemeral, including the ssh keys.

## Usage

    python3 do-spot-vpn.py create
    python3 do-spot-vpn.py list
    python3 do-spot-vpn.py delete <suffix>

## Environment variables

    DIGITALOCEAN_TOKEN
    TAILSCALE_AUTH_KEY

    export DIGITALOCEAN_TOKEN="your_digitalocean_token"
    export TAILSCALE_AUTH_KEY="your_tailscale_auth_key"

## Docker

    docker build -t do-spot-vpn .
    docker run -it --rm do-spot-vpn create
    docker run -it --rm do-spot-vpn list
    docker run -it --rm do-spot-vpn delete <suffix>
