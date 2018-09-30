#!/bin/bash

# Install ufw
apt-get -y install ufw

# Set default incoming policy
ufw default deny incoming

# On the OUTPUT chain, allow everything by default
# (including http/https requests to external monitors)
ufw default allow outgoing

# All related and established connections pass through
# (by default this is enabled on ufw)

# We can ssh to ARTEMIS only from the gateway VM
ufw allow from <GW_VM_IP> to any port 22 proto tcp

# We can ping the machine from anywhere
# (by default ufw enables ping requests)

# We can use https from certain access prefixes
# (incl. /32):
ufw allow from <ACCESS_PREFIX_1> to any port 443 proto tcp
# ...
ufw allow from <ACCESS_PREFIX_N> to any port 443 proto tcp

# [OPTIONAL] We can form i/eBGP sessions with one or more
# local routers
ufw allow from <ROUTER_1> to any port 179 proto tcp
# ...
ufw allow from <ROUTER_N> to any port 179 proto tcp

# Anything is allowed on the local interface
ufw allow in on lo to any

# Enable ufw
ufw enable

# [OPTIONAL] ufw disable, ufw status,
# ufw status numbered, ufw help...
