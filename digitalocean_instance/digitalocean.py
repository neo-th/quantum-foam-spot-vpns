import os
import time
import paramiko 
from pydo import Client

def gen_ephemeral_key(random_suffix):
    key = paramiko.RSAKey.generate(2048)
    key_file = f"id_ed25519-{random_suffix}"
    key.write_private_key_file(key_file)
    with open(f"{key_file}.pub", "w") as f:
        f.write(key.get_name() + " " + key.get_base64())

def push_ephemeral_key(client: Client, random_suffix: int):
    gen_ephemeral_key(random_suffix)
    req = {
        "name": f"ephemeral-key-{random_suffix}",
        "public_key": open(f"id_ed25519-{random_suffix}.pub").read().strip()
    }
    resp = client.ssh_keys.create(body=req)
    return resp["ssh_key"]["fingerprint"], resp["ssh_key"]["id"]

def create_droplet(client: Client, random_suffix: int, user_data_script: str):
    fingerprint, ssh_key_id = push_ephemeral_key(client, random_suffix)

    req = {
        "name": f"spot-vpn-{random_suffix}",
        "region": "nyc1",
        "size": "s-2vcpu-2gb-amd",
        "image": "ubuntu-22-04-x64",
        "user_data": user_data_script,
        "ssh_keys": [fingerprint]
    }
    resp = client.droplets.create(body=req)
    droplet_id = resp["droplet"]["id"]
    
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

def delete_droplet_and_keys(client: Client, droplet_id: str, suffix: str):
    print(f"Deleting Droplet {droplet_id}...")
    try:
        client.droplets.destroy(droplet_id=droplet_id)
        print("Droplet deleted on DigitalOcean.")
    except Exception as e:
        print(f"Error deleting droplet: {e}")

    print("Finding and deleting SSH key on DigitalOcean...")
    try:
        keys_resp = client.ssh_keys.list()
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
