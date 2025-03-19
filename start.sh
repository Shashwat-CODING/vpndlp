#!/bin/bash
set -e

# Load environment variables from .env file if it exists
if [ -f .env ]; then
    echo "Loading environment variables from .env file"
    export $(grep -v '^#' .env | xargs)
fi

# Set default VPN credentials if not set in environment
if [ -z "$VPN_USERNAME" ]; then
    export VPN_USERNAME="vpnuser"
    echo "Using default VPN username"
fi

if [ -z "$VPN_PASSWORD" ]; then
    export VPN_PASSWORD="vpnpass2025"
    echo "Using default VPN password"
fi

# Function to check current IP
check_ip() {
    echo "Current IP address:"
    IP_INFO=$(curl -s https://ipinfo.io/json)
    IP=$(echo $IP_INFO | grep -o '"ip": "[^"]*' | cut -d'"' -f4)
    COUNTRY=$(echo $IP_INFO | grep -o '"country": "[^"]*' | cut -d'"' -f4)
    REGION=$(echo $IP_INFO | grep -o '"region": "[^"]*' | cut -d'"' -f4)
    CITY=$(echo $IP_INFO | grep -o '"city": "[^"]*' | cut -d'"' -f4)
    ISP=$(echo $IP_INFO | grep -o '"org": "[^"]*' | cut -d'"' -f4)
    
    echo "IP: $IP"
    echo "Country: $COUNTRY"
    echo "Region: $REGION"
    echo "City: $CITY"
    echo "ISP: $ISP"
    
    # Log to persistent log file for Render logs
    if [ -n "$RENDER" ]; then
        echo "[$(date)] VPN STATUS - IP: $IP, Country: $COUNTRY, Region: $REGION, City: $CITY, ISP: $ISP" >> /var/log/vpn-status.log
        # Make sure this shows up in Render logs
        echo "[RENDER_VPN_STATUS] IP: $IP, Country: $COUNTRY, Region: $REGION, City: $CITY"
    fi
    
    # Check if IP is from India
    if [ "$COUNTRY" = "IN" ]; then
        echo "✓ Successfully connected through Indian IP address"
        if [ -n "$RENDER" ]; then
            echo "[RENDER_VPN_STATUS] ✓ SUCCESS: Connected through Indian IP ($REGION, $CITY)"
            # Create status file that can be checked by the app
            echo "CONNECTED_TO_INDIA=true" > /tmp/vpn_status
            echo "IP=$IP" >> /tmp/vpn_status
            echo "COUNTRY=$COUNTRY" >> /tmp/vpn_status
            echo "REGION=$REGION" >> /tmp/vpn_status
            echo "CITY=$CITY" >> /tmp/vpn_status
        fi
    else
        echo "⚠ Warning: Not connected through Indian IP address"
        if [ -n "$RENDER" ]; then
            echo "[RENDER_VPN_STATUS] ⚠ WARNING: Not connected through Indian IP (Current: $COUNTRY)"
            # Create status file that can be checked by the app
            echo "CONNECTED_TO_INDIA=false" > /tmp/vpn_status
            echo "IP=$IP" >> /tmp/vpn_status
            echo "COUNTRY=$COUNTRY" >> /tmp/vpn_status
        fi
    fi
}

# Check initial IP before VPN connection
echo "Initial IP before VPN connection:"
check_ip

# Look for VPN config in multiple locations
VPN_CONFIG_PATHS=(
    "/etc/openvpn/vpn-config.ovpn"
    "./vpn-config.ovpn"
    "/app/vpn-config.ovpn"
)

VPN_CONFIG_PATH=""
for path in "${VPN_CONFIG_PATHS[@]}"; do
    if [ -f "$path" ]; then
        VPN_CONFIG_PATH="$path"
        echo "Found VPN configuration at $VPN_CONFIG_PATH"
        break
    fi
done

if [ -n "$VPN_CONFIG_PATH" ]; then
    # Process the VPN config to replace environment variable placeholders
    echo "Substituting VPN credentials from environment variables..."
    # Create a temporary file
    TMP_CONFIG="/tmp/processed-vpn-config.ovpn"
    cp "$VPN_CONFIG_PATH" "$TMP_CONFIG"
    
    # Replace placeholders with actual values
    sed -i "s/##VPN_USERNAME##/$VPN_USERNAME/g" "$TMP_CONFIG"
    sed -i "s/##VPN_PASSWORD##/$VPN_PASSWORD/g" "$TMP_CONFIG"
    
    # Add additional configuration if needed
    # Make sure compression is enabled for better performance
    if ! grep -q "comp-lzo" "$TMP_CONFIG"; then
        echo "comp-lzo yes" >> "$TMP_CONFIG"
    fi
    
    # Use the processed config
    VPN_CONFIG_PATH="$TMP_CONFIG"
    echo "VPN config processed with credentials"
    
    echo "Starting OpenVPN connection..."
    # Start OpenVPN in the background
    openvpn --config "$VPN_CONFIG_PATH" --daemon
    
    # Give VPN a moment to connect
    echo "Waiting for VPN connection to establish..."
    MAX_ATTEMPTS=15
    CONNECTED=false
    
    for i in $(seq 1 $MAX_ATTEMPTS); do
        sleep 5
        if pgrep -x "openvpn" > /dev/null; then
            echo "OpenVPN process is running, checking IP..."
            check_ip
            echo "VPN connection established. Starting application..."
            CONNECTED=true
            break
        else
            echo "OpenVPN process not running. Attempt $i/$MAX_ATTEMPTS..."
            if [ $i -eq $MAX_ATTEMPTS ]; then
                echo "WARNING: OpenVPN failed to start. Continuing without VPN..."
            fi
        fi
    done
    
    # Clean up the temporary config file if it was created
    if [ -f "$TMP_CONFIG" ]; then
        rm -f "$TMP_CONFIG"
    fi
    
    # If connected to VPN successfully, verify we can access YouTube
    if [ "$CONNECTED" = true ]; then
        echo "Testing YouTube connectivity through VPN..."
        if curl -s --head --fail "https://www.youtube.com" > /dev/null; then
            echo "✓ Successfully connected to YouTube through VPN"
        else
            echo "⚠ WARNING: Connected to VPN but YouTube access may be restricted"
            
            # Try to restart VPN with different settings if YouTube is blocked
            echo "Trying alternative VPN connection method..."
            pkill -9 openvpn || true
            
            # Add UDP instead of TCP and try again
            TMP_CONFIG2="/tmp/alt-vpn-config.ovpn"
            cp "$VPN_CONFIG_PATH" "$TMP_CONFIG2"
            sed -i "s/proto tcp/proto udp/g" "$TMP_CONFIG2"
            
            openvpn --config "$TMP_CONFIG2" --daemon
            sleep 10
            
            if curl -s --head --fail "https://www.youtube.com" > /dev/null; then
                echo "✓ Successfully connected to YouTube with alternative VPN settings"
            else
                echo "⚠ WARNING: Still unable to connect to YouTube. Application may have limited functionality."
            fi
            
            rm -f "$TMP_CONFIG2"
        fi
    fi
else
    echo "No VPN configuration found at any of the expected locations."
    echo "Starting application without VPN..."
    echo "Application may have limited functionality for region-restricted content."
fi

# Create cache directory if it doesn't exist
CACHE_DIR=${CACHE_DIR:-"/tmp/youtube_audio_cache"}
mkdir -p "$CACHE_DIR"
echo "Created cache directory at $CACHE_DIR"

# Setup YouTube cookies file for authenticated access
echo "Setting up YouTube cookies..."
COOKIES_SOURCE_PATHS=(
    "./attached_assets/cookies.txt"
    "/app/attached_assets/cookies.txt"
)

for path in "${COOKIES_SOURCE_PATHS[@]}"; do
    if [ -f "$path" ]; then
        cp "$path" "./cookies.txt"
        echo "✓ Copied cookies from $path to application root"
        break
    fi
done

if [ -f "./cookies.txt" ]; then
    echo "✓ YouTube cookies file is ready"
else
    echo "⚠ WARNING: YouTube cookies file not found. Some content may be restricted."
fi

# Start the Flask application with gunicorn
echo "Starting Flask application..."
exec gunicorn --bind 0.0.0.0:5000 --workers 4 --timeout 120 --access-logfile - --error-logfile - main:app