# One-Click Deployment to Render with VPN Support

This application is fully pre-configured and ready for immediate deployment to Render with VPN support to route traffic through an Indian IP address.

## Simplified Deployment (Recommended)

### Using the Blueprint Method (One-Click)

1. Fork or clone this repository to your GitHub account
2. Login to [Render](https://render.com)
3. Click "New +" and select "Blueprint"
4. Connect your GitHub account and select this repository
5. Click "Apply" and Render will automatically:
   - Create the PostgreSQL database
   - Deploy the web service with VPN support
   - Set up all necessary environment variables
   - Configure the disk for VPN configuration

**That's it!** The application will be deployed with VPN support for Indian IP addresses.

## Pre-Configured Components

This repository includes:

- ✓ Ready-to-use VPN configuration (`vpn-config.ovpn`)
- ✓ Pre-set VPN credentials (`vpnuser`/`vpnpass2025`)
- ✓ Optimized Docker and Poetry configurations
- ✓ Render Blueprint configuration (`render.yaml`)
- ✓ Automatic VPN connection verification

## No Additional Setup Required

Unlike most VPN-enabled applications, this one requires no additional setup:

- No need to obtain a separate VPN configuration
- No need to manually upload VPN config files
- No need to set environment variables
- No need to restart services

## Verifying the Deployment

After deployment completes:

1. Access your application at `https://youtube-audio-player-xxxx.onrender.com` 
2. Visit the `/system-info` endpoint to verify:
   - The VPN is connected
   - You have an Indian IP address
   - YouTube content is accessible

## Alternative Deployment Methods

If you prefer more control, you can deploy using the Dashboard method:

### Docker Deployment via Dashboard

1. Login to your Render account
2. Create a new Web Service
3. Connect your Git repository
4. Select "Docker" as the Environment
5. Configure the service:
   - Name: youtube-audio-player
   - Environment: Docker
   - Branch: main
   - Health Check Path: `/health`
   - Disk: Create a new disk mounted at `/etc/openvpn` with 1GB space

No additional configuration is needed - the application is pre-configured with:
- Environment variables are pre-set in `render.yaml`
- VPN configuration is included in the repository
- Automatic VPN connection at startup

### Python Deployment via Dashboard

1. Login to your Render account
2. Create a new Web Service
3. Connect your Git repository
4. Select "Python" as the Environment
5. Configure the service:
   - Name: youtube-audio-player
   - Environment: Python
   - Build Command: `pip install poetry && poetry install`
   - Start Command: `./start.sh`
   - Health Check Path: `/health`
   - Disk: Create a new disk mounted at `/etc/openvpn` with 1GB space

## Customizing the Deployment

If you want to use your own VPN provider:

1. Replace `vpn-config.ovpn` with your own configuration
2. Update the VPN credentials in `render.yaml` and `.env`
3. Re-deploy the application

## Troubleshooting

If you encounter issues:

1. Check the logs in your Render dashboard for VPN connection messages
2. Visit the `/system-info` endpoint to verify your IP address
3. Ensure your repository includes the `vpn-config.ovpn` file
4. Check that the disk is properly mounted to `/etc/openvpn`

The application includes automatic fallback options if the VPN connection fails:
- Automatic retry with alternative protocols (UDP/TCP)
- Graceful degradation to continue functioning without VPN
- Detailed logging of connection attempts

## Advanced Configuration

For advanced customization, refer to:

- [VPN_SETUP_GUIDE.md](VPN_SETUP_GUIDE.md) - Detailed VPN configuration options
- Deployment settings in `render.yaml`
- VPN connection logic in `start.sh`