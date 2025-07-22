#!/bin/bash

# Start Home Assistant in development mode
echo "Starting Home Assistant for development..."

# Set up the config directory
mkdir -p /workspaces/home-assistant-zendure_local/config

# Copy devcontainer configuration to config
cp /workspaces/home-assistant-zendure_local/.devcontainer/configuration.yaml /workspaces/home-assistant-zendure_local/config/

# Create custom_components directory and link our integration
mkdir -p /workspaces/home-assistant-zendure_local/config/custom_components
ln -sf /workspaces/home-assistant-zendure_local/custom_components/zendure_local /workspaces/home-assistant-zendure_local/config/custom_components/

# Start Home Assistant
hass --config /workspaces/home-assistant-zendure_local/config --debug