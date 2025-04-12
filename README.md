# Hybrid Star-Mesh UAV Communication Network Simulation (WORK IN PROGRESS) 

This project simulates a resilient UAV (Unmanned Aerial Vehicle) command and control network using a hybrid star-mesh topology. The simulation leverages Docker containers integrated into a GNS3 network and uses Python to emulate UAV telemetry and command center (C2) communications.

## Overview

- **Hybrid Topology:**
  - **Star Component:** Each UAV sends telemetry data directly to a central Command Center.
  - **Mesh Component:** UAVs also broadcast telemetry to each other via multicast, enabling redundancy and relay of data if a direct link fails.
- **Key Features:**
  - Real-time UAV telemetry: Includes position, altitude, battery status, and optional frequency/channel information.
  - Data relaying: UAVs relay telemetry received from peers along with relay metadata.
  - Modular Python scripts leveraging threading to concurrently handle sending, broadcasting, and receiving.
  - Future enhancements planned for encryption and remote command/control for course correction.

## Components

### UAV Communication Script (`uav_comm.py`)
This script runs on each UAV container and performs the following:
- **Generates telemetry data** (e.g., GPS coordinates, altitude, battery level).
- **Sends direct telemetry** to the Command Center.
- **Broadcasts telemetry** via multicast for peer-to-peer sharing.
- **Listens for multicast messages** from other UAVs, and when received, **relays** them to the Command Center with additional metadata (relay hops).

### Command Center Receiver Script (`primary_c2_receiver.py`)
This script runs on the Command Center container and listens for:
- **Direct telemetry** (including any relayed messages) on a designated UDP port.
- **Multicast telemetry** from UAVs.
It then displays all incoming data along with any relay chain information.



**Requirements:**

Docker

GNS3 (for network simulation/integration)

Python 3.x + 

A Docker image (e.g., ubuntu:latest) with your shared scripts mounted (or a custom image with preinstalled Python)

Setup Docker Containers:

Create a shared volume containing the scripts.

Deploy Docker containers for UAV1, UAV2, UAV3, and Command Center.

Example commands (assuming the shared volume maps to /scripts inside each container):

**For each UAV:**

docker exec -it UAV1 bash -c "python3 /scripts/uav_comm.py UAV1"
docker exec -it UAV2 bash -c "python3 /scripts/uav_comm.py UAV2"
docker exec -it UAV3 bash -c "python3 /scripts/uav_comm.py UAV3"

**For the Command Center:**


docker exec -it CommandCenter bash -c "python3 /scripts/primary_c2_receiver.py"

**Usage**

Simulation Mode (Docker/GNS3):

Integrate the Docker containers into your GNS3 topology.

Connect the containers using a virtual switch in GNS3.

Observe real-time telemetry on the Command Center console, with data relayed from UAVs if applicable.

**Planned Enhancements:**

Adding encryption for secure communications.

Enhancing the Command Center to send out commands (via multicast or direct unicast) for UAV course correction or operational adjustments. (Already Implemented, fine tuning to come)

**Threading**

The Python scripts use the threading module to run multiple concurrent operations:

In the UAV script, threads are used to:

Send telemetry directly to the Command Center.

Broadcast telemetry via multicast.

Listen for and relay multicast messages from peers.

This allows for non-blocking, real-time operation.

**Future Work**
**Encryption:**
Future updates will incorporate encryption for secure communications.

**Adaptive Command Control:**
Adding mechanisms for the Command Center to compute and broadcast new operational parameters or course corrections to the UAVs.

**Dynamic Frequency Management:**
Potential integration of real frequency scanning and adaptive channel selection.

**License**
This project is licensed under the MIT License. See the LICENSE file for details.

**Acknowledgments**
This project was inspired by the need for resilient, real-time UAV communications in dynamic operational environments. Special thanks to the Docker, GNS3, and Python communities for providing the tools that make such simulations possible.


