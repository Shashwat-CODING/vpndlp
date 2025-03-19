# Pre-Configured VPN Setup with Indian IP Access

This application comes with a **fully pre-configured VPN setup** that is ready to deploy immediately. The VPN is configured to route traffic through Indian IP addresses for accessing region-restricted YouTube content.

## ✓ No Configuration Required!

Unlike most VPN-enabled applications, **no additional setup is required**:

- ✓ VPN configuration file is already included (`vpn-config.ovpn`)
- ✓ Authentication credentials are pre-configured (`vpnuser` / `vpnpass2025`)
- ✓ The startup script automatically handles the VPN connection
- ✓ Connection validation and fallback mechanisms are built-in

Simply deploy the application using the instructions in [RENDER_DEPLOYMENT.md](RENDER_DEPLOYMENT.md) and the VPN will be automatically configured.

## Verifying the VPN Connection

After deployment, you can verify that the VPN is working correctly:

1. Check the application logs for:
   - "VPN connection established" message
   - Confirmation of an Indian IP address
   - "Successfully connected to YouTube" message

2. Visit the `/system-info` endpoint in your browser, which will show:
   - Current external IP address (should be an Indian IP)
   - VPN connection status
   - Geographic location (should show India)
   - System details and connection information

## Advanced: Using Your Own VPN Provider

If you prefer to use your own VPN provider, you can replace the included configuration:

1. Obtain an OpenVPN configuration file (`.ovpn`) for an Indian server from your preferred provider
2. Ensure it includes all necessary certificates and authentication methods
3. Replace the existing `vpn-config.ovpn` file with your new configuration
4. Update the VPN credentials in both:
   - `render.yaml` (for new deployments)
   - Environment variables in your Render dashboard (for existing deployments)

### VPN Provider Requirements

For optimal performance, your VPN provider should have:

- Reliable servers in India with good uptime
- Strong bandwidth for streaming media
- Support for OpenVPN protocol
- No YouTube blocking or restrictions
- Stable connections for production use

### Formatting Your Own OpenVPN Configuration

If creating your own configuration, follow this format:

```
client
dev tun
proto udp
remote YOUR_INDIAN_SERVER_ADDRESS PORT
resolv-retry infinite
nobind
persist-key
persist-tun
remote-cert-tls server
cipher AES-256-CBC
verb 3

# Using environment variables for authentication
auth-user-pass
username ##VPN_USERNAME##
password ##VPN_PASSWORD##

<ca>
... (Your CA certificate) ...
</ca>

# Optional: Include client certificate if required
<cert>
... (Your client certificate) ...
</cert>

<key>
... (Your private key) ...
</key>

# Route all traffic through VPN
redirect-gateway def1

# DNS configuration
dhcp-option DNS 8.8.8.8
dhcp-option DNS 8.8.4.4

# Performance settings
keepalive 10 120
comp-lzo yes
```

## Troubleshooting VPN Connections

The application includes automatic fallback mechanisms:

1. If the initial VPN connection fails, it will:
   - Automatically retry up to 15 times
   - Switch between TCP and UDP protocols
   - Attempt alternative DNS configurations
   - Provide detailed logs of each attempt

2. If YouTube connectivity fails even with VPN:
   - Check if your VPN provider or IP range is blocked by YouTube
   - Try modifying the `vpn-config.ovpn` file to use a different server
   - Update the `start.sh` script to add additional connection parameters

3. If performance is poor:
   - Consider upgrading your Render service plan for better resources
   - Try a different VPN server with less congestion
   - Adjust the streaming quality settings in the application

## Security Best Practices

Even though this application comes pre-configured, you should consider these security enhancements for production use:

1. Change the default VPN credentials in your Render dashboard
2. Restrict access to the `/system-info` endpoint via authentication
3. Implement rate limiting on sensitive endpoints
4. Regularly rotate VPN credentials and certificates
5. Enable logging and monitoring for the VPN connection

## Advanced Configuration Options

The VPN connection behavior can be further customized by modifying:

- The `start.sh` script to change connection and retry parameters
- The `vpn-config.ovpn` file to adjust OpenVPN settings
- Environment variables to control VPN behavior:
  - `VPN_RETRY_ATTEMPTS`: Number of connection attempts (default: 15)
  - `VPN_CONNECT_TIMEOUT`: Seconds to wait for connection (default: 5)
  - `PREFERRED_REGION`: Target country code (default: IN)