#!/usr/bin/env bash
#
# Nmap script for detailed scanning, including vulscan and MQTT checks.
# Targets: 172.20.0.2, 172.20.0.3, 172.20.0.4

################################################################################
# 0) Setup
################################################################################
OUTPUT_DIR="Scans & Results"
mkdir -p "$OUTPUT_DIR"          
TARGETS="172.20.0.2 172.20.0.3 172.20.0.4"

################################################################################
# 1) Ping Scan (Host Discovery)
################################################################################
# -sn     = Host discovery only, no port scanning
# -oA     = Save output in .nmap, .gnmap, and .xml
echo ">>> [1/6] Starting Ping Scan..."
sudo nmap -sn $TARGETS -oA "$OUTPUT_DIR/ping_scan"

################################################################################
# 2) Full TCP Port Scan (SYN) on all ports
################################################################################
# -sS     = SYN scan (requires root)
# -p-     = All TCP ports (1–65535)
# -T4     = Faster timing template
echo ">>> [2/6] Starting Full TCP Port Scan (SYN)..."
sudo nmap -sS -p- -T4 $TARGETS -oA "$OUTPUT_DIR/tcp_full_scan"

################################################################################
# 3) Service & OS Detection
################################################################################
# -A      = OS detection, version detection, default NSE scripts, traceroute
# -O      = OS detection (redundant if -A is used, but shown for clarity)
# -sV     = Version detection (also included by -A)
# -T4     = Faster timing
echo ">>> [3/6] Starting Service & OS Detection..."
sudo nmap -A -O -sV -T4 $TARGETS -oA "$OUTPUT_DIR/service_os_detection"

################################################################################
# 4) Basic Vulnerability Scan with Default NSE (vuln scripts)
################################################################################
# --script=vuln = Executes a set of pre-defined vulnerability checks
echo ">>> [4/6] Starting Basic Vulnerability Scan (NSE: vuln)..."
sudo nmap -sV --script=vuln $TARGETS -oA "$OUTPUT_DIR/vuln_scan"

################################################################################
# 5) Extended NSE Scans
################################################################################
# Example 1: HTTP, SSL, UPnP
#   - "http*"     : all HTTP/web-related NSE scripts
#   - "ssl*"      : SSL/TLS detection, ciphers, etc.
#   - upnp-info   : info about UPnP services (common in IoT)
echo ">>> [5/6] Extended NSE Scans (HTTP, SSL, UPnP)..."
sudo nmap -sV \
  --script="http*,ssl*,upnp-info" \
  -p80,443,1900 \
  $TARGETS -oA "$OUTPUT_DIR/specialized_nse_scan"

# Example 2: MQTT scanning
#   - "mqtt-subscribe": checks for MQTT info, possible misconfigurations
# Port 1883 is common for MQTT
echo ">>> [5/6b] Extended NSE Scans (MQTT)..."
sudo nmap -sV \
  --script="mqtt-subscribe" \
  -p1883 \
  $TARGETS -oA "$OUTPUT_DIR/mqtt_nse_scan"

################################################################################
# 6) Vulscan-based Vulnerability Detection
################################################################################
# This step requires that you have installed or symlinked vulscan to:
#   /usr/share/nmap/scripts/vulscan
# See: https://github.com/scipag/vulscan
#
# -p-      = Scans all TCP ports again, but you can also limit to top ports
# -sV      = Version detection (needed for vulscan to identify potential issues)
# --script=vulscan/vulscan.nse = runs the main vulscan script
echo ">>> [6/6] Vulscan-based Vulnerability Scan..."
sudo nmap -sV -p- --script=vulscan/vulscan.nse \
  $TARGETS -oA "$OUTPUT_DIR/vulscan_results"

echo ">>> All Nmap scans completed! Outputs stored in '$OUTPUT_DIR' directory."
