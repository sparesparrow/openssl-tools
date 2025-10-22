#!/bin/bash

# Network Routing Setup Script
# This script configures routing for the ethernet networking setup

set -e

echo "Setting up network routing..."

# Enable IP forwarding (should already be enabled for Docker)
echo 1 > /proc/sys/net/ipv4/ip_forward

# Add static route to studijko network (192.168.201.0/24)
# Replace GATEWAY_IP with the actual IP address of the gateway/router that can reach 192.168.201.0/24
# This could be studijko's IP if it's directly connected, or another router IP
GATEWAY_IP="192.168.200.2"  # TODO: Replace with actual gateway IP to reach 192.168.201.0/24

# Add route to studijko network via enp7s0 (assuming studijko is reachable through the 192.168.200.0/24 network)
ip route add 192.168.201.0/24 via $GATEWAY_IP dev enp7s0 || echo "Route to 192.168.201.0/24 already exists or failed"

# Docker network routing - route Docker networks to studijko
# This assumes studijko is at 192.168.201.2 - adjust as needed
STUDIJKO_IP="192.168.201.2"  # TODO: Replace with studijko's actual IP

# Add routes for Docker networks to reach studijko
docker_networks=("172.17.0.0/16" "172.18.0.0/16" "172.19.0.0/16" "172.20.0.0/16")
for network in "${docker_networks[@]}"; do
    ip route add $network via $STUDIJKO_IP dev enp7s0 2>/dev/null || echo "Route for $network already exists or failed"
done

# iptables rules for routing (should already be set, but let's ensure)
iptables -t nat -C POSTROUTING -o enp5s0 -j MASQUERADE 2>/dev/null || iptables -t nat -A POSTROUTING -o enp5s0 -j MASQUERADE
iptables -C FORWARD -i enp7s0 -o enp5s0 -j ACCEPT 2>/dev/null || iptables -A FORWARD -i enp7s0 -o enp5s0 -j ACCEPT

# Allow forwarding from Docker networks to studijko network
iptables -C FORWARD -i br-+ -o enp7s0 -d 192.168.201.0/24 -j ACCEPT 2>/dev/null || iptables -A FORWARD -i br-+ -o enp7s0 -d 192.168.201.0/24 -j ACCEPT

echo "Network routing setup complete."
echo ""
echo "TODO: Update the following variables in this script:"
echo "  - GATEWAY_IP: IP address that can reach 192.168.201.0/24 network"
echo "  - STUDIJKO_IP: Actual IP address of studijko machine"
echo ""
echo "Current routes:"
ip route show