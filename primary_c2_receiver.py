#!/usr/bin/env python3
import socket
import ast
import threading

# Direct telemetry configuration
HOST = "0.0.0.0"  # Listen on all network interfaces
DIRECT_PORT = 9999  # Port for direct telemetry (including relayed data)

# Multicast configuration for UAV-to-UAV communication
MULTICAST_GROUP = "239.255.255.250"
MULTICAST_PORT = 5000


def receive_direct_telemetry():
    """Receive direct (and relayed) telemetry from UAVs on port 9999."""
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind((HOST, DIRECT_PORT))
    print(f"Command Center listening for direct telemetry on port {DIRECT_PORT}")
    while True:
        data, addr = sock.recvfrom(1024)
        try:
            telemetry = ast.literal_eval(data.decode('utf-8'))
        except Exception as e:
            print("Error parsing direct telemetry:", e)
            telemetry = {"raw_data": data.decode('utf-8')}
        print("\n--- Direct Telemetry ---")
        print(f"From {addr}:")
        print(f"  UAV ID  : {telemetry.get('id', 'Unknown')}")
        print(f"  Lat/Lon : {telemetry.get('lat', 'N/A')}, {telemetry.get('lon', 'N/A')}")
        print(f"  Alt     : {telemetry.get('alt', 'N/A')} m")
        print(f"  Battery : {telemetry.get('battery', 'N/A')}%")
        print(f"  Channel : {telemetry.get('channel', 'None')}")


def receive_multicast_telemetry():
    """Listen for multicast telemetry directly from UAVs."""
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock.bind(('', MULTICAST_PORT))

    mreq = socket.inet_aton(MULTICAST_GROUP) + socket.inet_aton("0.0.0.0")
    sock.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, mreq)
    print(f"Command Center listening for multicast telemetry on {MULTICAST_GROUP}:{MULTICAST_PORT}")

    while True:
        data, addr = sock.recvfrom(1024)
        try:
            telemetry = ast.literal_eval(data.decode('utf-8'))
        except Exception as e:
            print("Error parsing multicast telemetry:", e)
            telemetry = {"raw_data": data.decode('utf-8')}
        print("\n+++ Multicast Telemetry +++")
        print(f"From {addr}:")
        print(f"  UAV ID  : {telemetry.get('id', 'Unknown')}")
        print(f"  Lat/Lon : {telemetry.get('lat', 'N/A')}, {telemetry.get('lon', 'N/A')}")
        print(f"  Alt     : {telemetry.get('alt', 'N/A')} m")
        print(f"  Battery : {telemetry.get('battery', 'N/A')}%")
        print(f"  Channel : {telemetry.get('channel', 'None')}")


if __name__ == "__main__":
    # Start threads to concurrently listen for both direct and multicast telemetry.
    direct_thread = threading.Thread(target=receive_direct_telemetry, daemon=True)
    multicast_thread = threading.Thread(target=receive_multicast_telemetry, daemon=True)

    direct_thread.start()
    multicast_thread.start()

    # Keep the main thread running.
    try:
        while True:
            pass
    except KeyboardInterrupt:
        print("\nCommand Center shutting down.")
