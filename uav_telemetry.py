#!/usr/bin/env python3
import socket
import time
import random
import sys
import threading
import ast


if len(sys.argv) < 2:
    print("Usage: python3 uav_telemetry.py <UAV_ID>")
    sys.exit(1)

UAV_ID = sys.argv[1]

# Direct telemetry configuration (to Command Center)
# Set C2_IP to the Command Center container’s IP or use its container name (if Docker DNS is enabled).
C2_IP = "172.18.0.5"
C2_PORT = 9999  # Port for direct telemetry

# Multicast configuration for UAV-to-UAV communication
MULTICAST_GROUP = "239.255.255.250"
MULTICAST_PORT = 5000


def generate_telemetry():
    """
    Generate simulated telemetry data.
    You can later update the "channel" value dynamically.
    """
    telemetry = {
        "id": UAV_ID,
        "lat": round(40.7128 + random.uniform(-0.05, 0.05), 4),
        "lon": round(-74.0060 + random.uniform(-0.05, 0.05), 4),
        "alt": random.randint(100, 500),
        "battery": random.randint(20, 100),
        "channel": None  # Not set; update if you integrate frequency scanning data.
    }
    return str(telemetry)


def send_to_command_center():
    """Send own telemetry data directly to the Command Center every 5 seconds."""
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    while True:
        message = generate_telemetry()
        sock.sendto(message.encode('utf-8'), (C2_IP, C2_PORT))
        print(f"{UAV_ID} sent to CC:", message)
        time.sleep(5)


def send_direct_broadcast():
    """Broadcast own telemetry via multicast for peer-to-peer sharing every 5 seconds."""
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
    # Set TTL = 1 to ensure multicast packets remain on the local network.
    sock.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, 1)
    while True:
        message = generate_telemetry()
        sock.sendto(message.encode('utf-8'), (MULTICAST_GROUP, MULTICAST_PORT))
        print(f"{UAV_ID} broadcasted on multicast:", message)
        time.sleep(5)


def listen_to_multicast():
    """
    Listen for multicast messages from other UAVs.
    When a message is received, if it’s from a peer, relay it to the Command Center.
    """
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock.bind(('', MULTICAST_PORT))
    mreq = socket.inet_aton(MULTICAST_GROUP) + socket.inet_aton("0.0.0.0")
    sock.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, mreq)

    # Separate socket for relaying messages
    relay_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    while True:
        data, addr = sock.recvfrom(1024)
        try:
            telem = ast.literal_eval(data.decode('utf-8'))
            if telem.get("id") != UAV_ID:  # Only process messages from other UAVs
                print(f"{UAV_ID} received multicast from {telem.get('id')}: {telem}")
                # Relay the received message to the Command Center
                relay_sock.sendto(data, (C2_IP, C2_PORT))
        except Exception as e:
            print(f"{UAV_ID} error parsing multicast:", e)


if __name__ == "__main__":
    # Start threads for each communication function.
    threading.Thread(target=send_to_command_center, daemon=True).start()
    threading.Thread(target=send_direct_broadcast, daemon=True).start()
    threading.Thread(target=listen_to_multicast, daemon=True).start()

    # Keep the main thread alive.
    while True:
        time.sleep(1)

