# YouTube Audio Player with VPN Support

A Flask-based web application that allows you to stream audio from YouTube videos through a VPN connection. This implementation specifically targets routing traffic through Indian IP addresses to access region-specific content.

## Features

- Stream audio from YouTube videos
- OpenVPN integration for routing traffic through Indian IP addresses
- Resilient connection handling with automatic retries
- Caching of audio streams for better performance
- Playlist management system
- Responsive web interface

## Ready to Deploy!

This application is pre-configured and ready to deploy immediately. We've included:

- ✓ Pre-configured VPN setup with Indian servers
- ✓ Ready-to-use authentication credentials 
- ✓ Deployment configuration for Render
- ✓ Optimized Docker and Poetry configurations
- ✓ Database setup with SQLAlchemy

## One-Click Deployment to Render

The fastest way to deploy this application:

1. Fork or clone this repository to your GitHub account
2. Login to [Render](https://render.com)
3. Click "New +" and select "Blueprint"
4. Connect your GitHub account and select this repository
5. Click "Apply" and Render will automatically:
   - Create the PostgreSQL database
   - Deploy the web service with VPN support
   - Set up all necessary environment variables
   - Configure the disk for VPN configuration

The application is pre-configured to route traffic through Indian IP addresses.

## Local Development Setup

You can set up this project using either Poetry (recommended) or pip.

### Option 1: Using Poetry (Recommended)

1. Clone this repository
2. Install Poetry if you haven't already:
   ```
   pip install poetry
   ```
3. Install dependencies:
   ```
   poetry install
   ```
4. Activate the virtual environment:
   ```
   poetry shell
   ```
5. Run the application:
   ```
   python main.py
   ```

### Option 2: Using Pip

1. Clone this repository
2. Create a virtual environment and activate it:
   ```
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```
3. Install dependencies:
   ```
   pip install -r render_requirements.txt
   ```
4. Run the application:
   ```
   python main.py
   ```

## VPN Configuration

This application comes with a pre-configured OpenVPN setup for Indian servers. The credentials are:

- Username: `vpnuser`
- Password: `vpnpass2025`

If you want to use your own VPN provider, simply replace the `vpn-config.ovpn` file with your own configuration.

## Architecture

- **Flask Backend**: Handles requests and YouTube data extraction
- **yt-dlp**: Extracts audio streams from YouTube
- **OpenVPN**: Routes traffic through Indian IP addresses
- **SQLAlchemy**: Database ORM for playlist and cache management
- **Gunicorn**: WSGI HTTP server for production

## Database Schema

The application uses the following database models:

- **Playlist**: Stores user-created playlists
- **PlaylistItem**: Stores YouTube videos within playlists
- **AudioCache**: Tracks cached audio files for better performance

## Usage

1. Open the web application in your browser
2. Enter a YouTube URL in the input field
3. Click "Play" to stream the audio
4. Optionally add the current track to a playlist

## Production Deployment Options

For customized deployment, refer to:

- [VPN_SETUP_GUIDE.md](VPN_SETUP_GUIDE.md) - Detailed VPN setup instructions
- [RENDER_DEPLOYMENT.md](RENDER_DEPLOYMENT.md) - Advanced Render deployment options

## Troubleshooting

- If you encounter VPN connection issues, check the Render logs at `/system-info`
- For YouTube extraction errors, verify that your VPN is correctly routing traffic through an Indian IP

## License

[MIT License](LICENSE)

## Acknowledgements

- [yt-dlp](https://github.com/yt-dlp/yt-dlp) for YouTube extraction
- [Flask](https://flask.palletsprojects.com/) for the web framework
- [OpenVPN](https://openvpn.net/) for VPN connectivity