# Master Thesis: Security Analysis of Smart Home Systems: Augmenting security tools with generative AI in a simulated environment

## Project Overview

This project is based on my Master's thesis:  
**Security Analysis of Smart Home Systems: Augmenting security tools with generative AI in a simulated environment**

The goal of the project is to investigate how generative AI models can detect and analyze security vulnerabilities in smart home systems. A realistic test environment was built using Docker containers to simulate a smart home setup with intentionally embedded security issues.

> **Note:** All development and testing were performed on an **Ubuntu** environment. Steps and commands (especially related to network configuration) might differ on other operating systems.

## Project Components

The environment consists of several Docker containers that simulate the following components:

- **Server Container**  
  Provides a REST API (built with Flask) for controlling and monitoring a simulated smart light bulb (on/off). The server translates HTTP requests into MQTT messages.

- **Client Container**  
  Simulates a smart home light bulb that listens for MQTT messages (via the MQTT broker) and updates its status accordingly.

- **Mosquitto Container**  
  Hosts the MQTT broker (Mosquitto) to enable communication between the server and client containers.

- **Kali Linux Container (Optional)**  
  Intended for security testing and equipped with tools like Nmap and Wireshark. Due to certain limitations, security testing is performed directly on the host.

- **AI REST API**  
  Located in the `api` folder, it communicates with generative AI models (e.g., OpenAI or Gemini) to process and analyze network scan results from tools such as Wireshark and Nmap.

- **Scans & Results**  
  Stores all scan outputs and processed results for further analysis.

## Features

- **Realistic Network Simulation:**  
  Uses a macvlan network to assign each container its own IP and MAC address, mimicking physical devices in a smart home.

- **Container Communication:**  
  Server and client communicate over MQTT. The server also exposes a REST API for remote control.

- **Security Vulnerability Simulation:**  
  The environment intentionally includes common IoT vulnerabilities (e.g., open ports, hardcoded credentials, unencrypted communication) for testing purposes.

- **AI Assisted Analysis:**  
  Integration with generative AI models to automatically process and interpret scan results.

## Prerequisites

Before running the project, make sure that:

- **Docker & Docker Compose** are installed on your system.
- A **macvlan network** is set up to simulate a realistic network environment.
- **Nmap** is installed
- **Wireshark** and TShark is installed
  
> **Note:** By default, Docker does not allow communication between the host and containers in a macvlan network. To enable this, an additional macvlan interface must be created on the host.


## Setting Up the macvlan Network

1. **Identify your Physical Network Interface**  
   Run the following command to list your network interfaces (e.g., `enp0s3`, `eth0`, or `wlan0`):
  ```bash
ip addr
```

2. **Create the macvlan Network**  
  Replace enp0s3 with your actual interface name if necessary:
 ```bash
docker network create -d macvlan \
  --subnet=172.20.0.0/16 \
  --gateway=172.20.0.1 \
  -o parent=enp0s3 smarthome_macvlan
```

3. **Enabling Host to Container Communication**

   By default, the host cannot communicate with containers on a macvlan network, because the communication in the macvlan is isolated. To control the smart light bulb from your host via a POST request, create an additional macvlan interface on your host:

```bash
ip link add macvlan_host link enp0s3 type macvlan mode bridge
ip addr add 172.20.0.1/24 dev macvlan_host
ip link set macvlan_host up
```

## API Configuration

The AI API requires API keys for the generative AI models. These keys must be provided via environment variables. In the api folder, there is a config.py file that loads the API keys from a .env file. Create a .env file in the root directory of the repository with the following content:

 ```bash
OPENAI_API_KEY=your-openai-api-key
GEMINI_API_KEY=your-gemini-api-key
```

Replace your-openai-api-key and your-gemini-api-key with your actual API keys.


## Running the Environment

1. **Clone the Repository**  
 ```bash
git clone https://github.com/TimK011/master_thesis_smart_home.git
cd master_thesis_smart_home
```

2. **Build and Start the Containers** 
```bash
docker-compose up --build
```

3. **Interact with the REST API**
   The server container exposes its API on port 5001. You can use Postman or any other HTTP client to:
```bash
Check bulb status: GET /status
Turn on the bulb: POST /turn_on
Turn off the bulb: POST /turn_off
```


## Using the NMap Script

**Nmap Scanning Script**  
The provided Nmap script performs detailed network scans and vulnerability checks. It carries out:
```bash
Ping Scan (Host Discovery)
Full TCP Port Scan (SYN)
Service & OS Detection
Basic Vulnerability Scan with Default NSE Scripts
Extended NSE Scans (HTTP, SSL, UPnP, MQTT)
Vulscan based Vulnerability Detection
```

**How to Use the Nmap Script:**

1. **Make the Script Executable:**  
 ```bash
chmod +x nmap_scan.sh
```

2. **Run the Script with Root Privileges:**  
 ```bash
sudo ./nmap_scan.sh
```    


3. **Review the Results:**  
Scan outputs are saved in the Scans & Results directory in multiple formats.


## Using Wireshark to CSV Conversion Script

The Wireshark script converts a PCAP file into CSV format suitable as input for the AI REST API.

**How to Use the Wireshark to CSV Script:**

1. **Prerequisites:**  

- Ensure that TShark is installed. 
- Set the variable tshark_path in the script to the full path of your TShark executable (e.g., /usr/bin/tshark).

2. **Run the script from the command line with the following syntax:**

 ```bash
python3 wireshark_to_csv.py input.pcap output_base.csv
```    
- input.pcap: The PCAP file exported by Wireshark.
- output_base.csv: The base name for the output CSV files (e.g., if you use output.csv, the script will generate output_1.csv, output_2.csv, etc.).
   
3. **Output:**
  The script will generate 5 CSV files containing the converted data. Each CSV includes a header that maps short field names (e.g., f1, f2, ...) to the original field names.

Example:

 ```bash
python3 wireshark_to_csv.py capture.pcap wireshark_output.csv
```    

