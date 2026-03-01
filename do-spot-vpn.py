import os
import time
import random
import argparse
import paramiko 
from pydo import Client
from sqlite import insert_vpn, get_vpn, delete_vpn

def gen_ephemeral_key(random_suffix):
    key = paramiko.RSAKey.generate(2048)
    key_file = f"id_ed25519-{random_suffix}"
    key.write_private_key_file(key_file)
    with open(f"{key_file}.pub", "w") as f:
        f.write(key.get_name() + " " + key.get_base64())

def push_ephemeral_key(client, random_suffix):
    gen_ephemeral_key(random_suffix)
    req = {
        "name": f"ephemeral-key-{random_suffix}",
        "public_key": open(f"id_ed25519-{random_suffix}.pub").read().strip()
    }
    resp = client.ssh_keys.create(body=req)
    # The API returns ssh_key object
    return resp["ssh_key"]["fingerprint"], resp["ssh_key"]["id"]

def create_droplet(client, random_suffix, auth_key):
    fingerprint, ssh_key_id = push_ephemeral_key(client, random_suffix)

    user_data_script = f"""#cloud-config
    runcmd:
        - sysctl -w net.ipv4.ip_forward=1
        - sysctl -w net.ipv6.conf.all.forwarding=1
        - curl -fsSL https://tailscale.com/install.sh | sh
        - echo {auth_key} > /etc/tailscale-authkey
        - chmod 600 /etc/tailscale-authkey
        - tailscale up --auth-key=file:/etc/tailscale-authkey --advertise-exit-node
    """

    req = {
        "name": f"spot-vpn-{random_suffix}",
        "region": "nyc1",
        "size": "s-2vcpu-2gb-amd",
        "image": "ubuntu-22-04-x64",
        "user_data": user_data_script,
        "ssh_keys": [fingerprint]
    }
    resp = client.droplets.create(body=req)
    #print(resp)
    droplet_id = resp["droplet"]["id"]
    
    # Wait for the droplet to be active and have an IP address
    print(f"Waiting for droplet {droplet_id} to be active...")
    while True:
        droplet = client.droplets.get(droplet_id=droplet_id)["droplet"]
        if droplet["status"] == "active" and droplet["networks"]["v4"]:
            ip_address = droplet["networks"]["v4"][0]["ip_address"]
            print(f"Droplet {droplet_id} is active. IP address: {ip_address}")
            break
        print("Droplet not yet active, waiting 5 seconds...")
        time.sleep(5)
        
    return ip_address, droplet_id

def cmd_create(args):
    """Create a new VPN droplet."""
    if os.environ.get("TAILSCALE_AUTH_KEY") is None or os.environ.get("DIGITALOCEAN_TOKEN") is None:
        print("Error: Please set TAILSCALE_AUTH_KEY and DIGITALOCEAN_TOKEN environment variables")
        return

    client = Client(token=os.environ.get("DIGITALOCEAN_TOKEN"))
    auth_key = os.environ.get("TAILSCALE_AUTH_KEY")
    random_suffix = random.randint(1000, 9999)
    
    ip_address, droplet_id = create_droplet(client, random_suffix, auth_key)
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
        # IP, Droplet ID, Suffix, Timestamp
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
    
    print(f"Deleting Droplet {droplet_id}...")
    try:
        client.droplets.destroy(droplet_id=droplet_id)
        print("Droplet deleted on DigitalOcean.")
    except Exception as e:
        print(f"Error deleting droplet: {e}")

    print("Finding and deleting SSH key on DigitalOcean...")
    try:
        # Check matching ssh keys
        keys_resp = client.ssh_keys.list()
        # the response structure depends on pydo, usually keys_resp['ssh_keys']
        keys = keys_resp.get("ssh_keys", [])
        for key in keys:
            if key["name"] == f"ephemeral-key-{suffix}":
                client.ssh_keys.delete(ssh_key_identifier=key["id"])
                print(f"Deleted SSH key '{key['name']}' on DigitalOcean.")
                break
    except Exception as e:
        print(f"Error deleting SSH key from DO: {e}")

    try:
        key_file = f"id_ed25519-{suffix}"
        if os.path.exists(key_file):
            os.remove(key_file)
        if os.path.exists(f"{key_file}.pub"):
            os.remove(f"{key_file}.pub")
        print("Deleted local SSH key files.")
    except Exception as e:
        print(f"Error removing local key files: {e}")

    print("Removing VPN record from database...")
    delete_vpn(ip_address, str(droplet_id), str(suffix))
    print(f"VPN with suffix {suffix} deleted successfully.")

def main():
    parser = argparse.ArgumentParser(description="Manage DigitalOcean spot VPNs with Tailscale")
    subparsers = parser.add_subparsers(dest="command", help="Available commands")
    subparsers.required = True

    # command: create
    parser_create = subparsers.add_parser("create", help="Create a new VPN droplet")
    parser_create.set_defaults(func=cmd_create)

    # command: list
    parser_list = subparsers.add_parser("list", help="List active VPN droplets")
    parser_list.set_defaults(func=cmd_list)

    # command: delete
    parser_delete = subparsers.add_parser("delete", help="Delete a VPN droplet")
    parser_delete.add_argument("suffix", help="The 4-digit suffix of the VPN to delete")
    parser_delete.set_defaults(func=cmd_delete)

    args = parser.parse_args()
    args.func(args)

if __name__ == "__main__":
    main()
