def get_tailscale_user_data(auth_key: str) -> str:
    """Returns the cloud-config user data script for installing Tailscale."""
    return f"""#cloud-config
runcmd:
    - sysctl -w net.ipv4.ip_forward=1
    - sysctl -w net.ipv6.conf.all.forwarding=1
    - curl -fsSL https://tailscale.com/install.sh | sh
    - echo {auth_key} > /etc/tailscale-authkey
    - chmod 600 /etc/tailscale-authkey
    - tailscale up --auth-key=file:/etc/tailscale-authkey --advertise-exit-node
"""
