import os
import random
import argparse
from pydo import Client

from digitalocean_instance.digitalocean import create_droplet, delete_droplet_and_keys
from tailscale_vpn.tailscale import get_tailscale_user_data
from db.sqlite import insert_vpn, get_vpn, delete_vpn

def cmd_create(args):
    """Create a new Spot VPN."""
    if os.environ.get("TAILSCALE_AUTH_KEY") is None or os.environ.get("DIGITALOCEAN_TOKEN") is None:
        print("Error: Please set TAILSCALE_AUTH_KEY and DIGITALOCEAN_TOKEN environment variables")
        return

    client = Client(token=os.environ.get("DIGITALOCEAN_TOKEN"))
    auth_key = os.environ.get("TAILSCALE_AUTH_KEY")
    random_suffix = random.randint(1000, 9999)
    
    # We only have tailscale for now
    user_data_script = get_tailscale_user_data(auth_key)
    
    ip_address, droplet_id = create_droplet(client, random_suffix, user_data_script, args.region, args.size, args.image)
    print(f"Tailscale VPN configured on {ip_address}")
    insert_vpn(ip_address, str(droplet_id), str(random_suffix), args.provider, args.region)
    print(f"VPN successfully created! Suffix: {random_suffix}")

def cmd_list(args):
    """List active Spot VPNs."""
    vpns = get_vpn()
    if not vpns:
        print("No active spot VPNs found.")
        return
        
    print(f"{'IP Address':<16} | {'Droplet ID':<12} | {'Suffix':<8} | {'Provider':<12} | {'Region':<12} | {'Created At'}")
    print("-" * 101)
    for vpn in vpns:
        print(f"{vpn[0]:<16} | {vpn[1]:<12} | {vpn[2]:<8} | {vpn[3]:<12} | {vpn[4]:<12} | {vpn[5]}")

def cmd_delete(args):
    """Delete a Spot VPN."""
    if os.environ.get("DIGITALOCEAN_TOKEN") is None:
        print("Error: Please set DIGITALOCEAN_TOKEN environment variable")
        return

    vpns = get_vpn()
    target = None
    if vpns:
        for vpn in vpns:
            if vpn[2] == str(args.suffix):
                target = vpn
                break
            
    if not target:
        print(f"No Spot VPN found with suffix {args.suffix}")
        return

    ip_address, id, random_suffix, provider, region, created_at = target
    client = Client(token=os.environ.get("DIGITALOCEAN_TOKEN"))
    
    delete_droplet_and_keys(client, id, random_suffix)

    print("Removing VPN record from database...")
    delete_vpn(ip_address, str(id), str(random_suffix))
    print(f"Spot VPN with suffix {random_suffix} deleted successfully.")

def run_cli():
    parser = argparse.ArgumentParser(description="Manage spot VPNs")
    subparsers = parser.add_subparsers(dest="command", help="Available commands")
    subparsers.required = True

    parser_create = subparsers.add_parser("create", help="Create a new spot VPN")
    parser_create.add_argument("--provider", help="The cloud provider to use", choices=["digitalocean", "gcp", "aws"], default="digitalocean")
    parser_create.add_argument("--region", help="The region to use", default="nyc3")
    parser_create.add_argument("--size", help="The size of the droplet", default="s-2vcpu-4gb")
    parser_create.add_argument("--image", help="The image to use", default="ubuntu-22-04-x64")
    parser_create.set_defaults(func=cmd_create)

    parser_list = subparsers.add_parser("list", help="List active spot VPNs")
    parser_list.set_defaults(func=cmd_list)

    parser_delete = subparsers.add_parser("delete", help="Delete a spot VPN")
    parser_delete.add_argument("suffix", help="The 4-digit suffix of the VPN to delete")
    parser_delete.set_defaults(func=cmd_delete)

    args = parser.parse_args()
    args.func(args)
