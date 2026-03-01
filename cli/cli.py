import os
import random
import argparse
from pydo import Client

from digitalocean_instance.digitalocean import create_droplet, delete_droplet_and_keys
from tailscale_vpn.tailscale import get_tailscale_user_data
from db.sqlite import insert_vpn, get_vpn, delete_vpn

def cmd_create(args):
    """Create a new VPN droplet."""
    if os.environ.get("TAILSCALE_AUTH_KEY") is None or os.environ.get("DIGITALOCEAN_TOKEN") is None:
        print("Error: Please set TAILSCALE_AUTH_KEY and DIGITALOCEAN_TOKEN environment variables")
        return

    client = Client(token=os.environ.get("DIGITALOCEAN_TOKEN"))
    auth_key = os.environ.get("TAILSCALE_AUTH_KEY")
    random_suffix = random.randint(1000, 9999)
    
    # We only have tailscale for now
    user_data_script = get_tailscale_user_data(auth_key)
    
    ip_address, droplet_id = create_droplet(client, random_suffix, user_data_script)
    print(f"Tailscale VPN configured on {ip_address}")
    insert_vpn(ip_address, str(droplet_id), str(random_suffix))
    print(f"VPN successfully created! Suffix: {random_suffix}")

def cmd_list(args):
    """List active VPN droplets."""
    vpns = get_vpn()
    if not vpns:
        print("No active VPNs found.")
        return
        
    print(f"{'IP Address':<16} | {'Droplet ID':<12} | {'Suffix':<8} | {'Created At'}")
    print("-" * 65)
    for vpn in vpns:
        print(f"{vpn[0]:<16} | {vpn[1]:<12} | {vpn[2]:<8} | {vpn[3]}")

def cmd_delete(args):
    """Delete a VPN droplet."""
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
        print(f"No VPN found with suffix {args.suffix}")
        return

    ip_address, droplet_id, suffix, _ = target
    client = Client(token=os.environ.get("DIGITALOCEAN_TOKEN"))
    
    delete_droplet_and_keys(client, droplet_id, suffix)

    print("Removing VPN record from database...")
    delete_vpn(ip_address, str(droplet_id), str(suffix))
    print(f"VPN with suffix {suffix} deleted successfully.")

def run_cli():
    parser = argparse.ArgumentParser(description="Manage DigitalOcean spot VPNs")
    subparsers = parser.add_subparsers(dest="command", help="Available commands")
    subparsers.required = True

    parser_create = subparsers.add_parser("create", help="Create a new VPN droplet")
    parser_create.set_defaults(func=cmd_create)

    parser_list = subparsers.add_parser("list", help="List active VPN droplets")
    parser_list.set_defaults(func=cmd_list)

    parser_delete = subparsers.add_parser("delete", help="Delete a VPN droplet")
    parser_delete.add_argument("suffix", help="The 4-digit suffix of the VPN to delete")
    parser_delete.set_defaults(func=cmd_delete)

    args = parser.parse_args()
    args.func(args)
