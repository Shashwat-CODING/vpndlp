import os
import logging
import platform
import socket
import requests
import subprocess
import datetime
from flask import Flask, render_template, request, jsonify
from utils import validate_youtube_url, get_audio_stream, ensure_cookies_file

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET", "dev_secret_key")

# Initialize cookies file at startup
cookie_file = ensure_cookies_file()
if cookie_file:
    logger.info(f"YouTube cookies initialized from: {cookie_file}")
else:
    logger.warning("YouTube cookies could not be initialized")

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/system-info')
def system_info():
    """Get system information, including IP and VPN status (admin use only)"""
    try:
        # Get IP address from external service
        external_ip = "Unknown"
        try:
            external_ip = requests.get('https://httpbin.org/ip', timeout=5).json()['origin']
        except Exception as e:
            external_ip = f"Error getting external IP: {str(e)}"

        # Get system information
        info = {
            "hostname": socket.gethostname(),
            "platform": platform.platform(),
            "python_version": platform.python_version(),
            "external_ip": external_ip,
            "environment": "Production" if os.environ.get("RENDER") else "Development"
        }
        
        # Check for OpenVPN process
        vpn_status = "Not running"
        if platform.system() != "Windows":  # Skip on Windows
            try:
                result = subprocess.run(["pgrep", "openvpn"], capture_output=True, text=True)
                vpn_status = "Running" if result.stdout.strip() else "Not running"
            except Exception as e:
                vpn_status = f"Error checking VPN status: {str(e)}"
        
        info["vpn_status"] = vpn_status
        
        # Try a geo-location check to verify IP location
        try:
            geo_response = requests.get('https://ipinfo.io', timeout=5).json()
            info["ip_country"] = geo_response.get('country', 'Unknown')
            info["ip_region"] = geo_response.get('region', 'Unknown')
            info["ip_city"] = geo_response.get('city', 'Unknown')
        except Exception as e:
            info["geo_error"] = str(e)
        
        return jsonify(info)
    except Exception as e:
        logger.error(f"Error getting system info: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route('/play', methods=['POST'])
def play_audio():
    url = request.form.get('url')

    if not url:
        return jsonify({'error': 'No URL provided'}), 400

    if not validate_youtube_url(url):
        return jsonify({'error': 'Invalid YouTube URL'}), 400

    try:
        # Log the request with detailed information
        logger.info(f"Processing YouTube URL: {url}")
        
        # Check VPN status if in production
        if os.environ.get("RENDER"):
            try:
                result = subprocess.run(["pgrep", "openvpn"], capture_output=True, text=True)
                vpn_running = bool(result.stdout.strip())
                logger.info(f"VPN status before extraction: {'Running' if vpn_running else 'Not running'}")
            except Exception as e:
                logger.warning(f"Could not check VPN status: {str(e)}")
        
        # Get direct stream URL
        stream_url, title = get_audio_stream(url)
        
        if not stream_url:
            raise ValueError("Failed to obtain audio stream URL")
            
        logger.info(f"Successfully obtained stream for '{title}'")
        return jsonify({
            'audio_path': stream_url,
            'title': title
        })

    except Exception as e:
        logger.error(f"Error processing URL {url}: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/vpn-status')
def vpn_status():
    """Endpoint to specifically check VPN status for Render deployment"""
    try:
        # Check if OpenVPN process is running
        vpn_running = False
        try:
            result = subprocess.run(["pgrep", "openvpn"], capture_output=True, text=True)
            vpn_running = bool(result.stdout.strip())
        except Exception as e:
            return jsonify({"error": f"Failed to check VPN process: {str(e)}"}), 500
        
        # Get current IP information
        try:
            ip_info = requests.get('https://ipinfo.io/json', timeout=5).json()
            
            # Check if we're connected through an Indian IP
            is_indian_ip = ip_info.get('country') == 'IN'
            
            status_message = ""
            if is_indian_ip:
                status_message = f"Connected through Indian IP: {ip_info.get('city', 'Unknown')}, {ip_info.get('region', 'Unknown')}"
                logger.info(f"[RENDER_VPN_STATUS] ✓ {status_message}")
            else:
                status_message = f"Not connected through Indian IP. Current country: {ip_info.get('country', 'Unknown')}"
                logger.warning(f"[RENDER_VPN_STATUS] ⚠ {status_message}")
            
            # Build response
            response = {
                "vpn_process_running": vpn_running,
                "connected_to_india": is_indian_ip,
                "ip": ip_info.get('ip', 'Unknown'),
                "country": ip_info.get('country', 'Unknown'),
                "region": ip_info.get('region', 'Unknown'),
                "city": ip_info.get('city', 'Unknown'),
                "status_message": status_message,
                "timestamp": str(datetime.datetime.now())
            }
            
            return jsonify(response)
        except Exception as e:
            return jsonify({
                "vpn_process_running": vpn_running,
                "error": f"Failed to get IP information: {str(e)}",
                "timestamp": str(datetime.datetime.now())
            }), 500
            
    except Exception as e:
        logger.error(f"VPN status check failed: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route('/health')
def health_check():
    """Detailed health check endpoint for Render"""
    try:
        # Check if we're in a production environment
        is_production = bool(os.environ.get("RENDER"))
        
        # Build response with basic health info
        response = {
            "status": "healthy",
            "environment": "Production" if is_production else "Development",
            "timestamp": str(datetime.datetime.now()),
            "cookies_status": "Available" if os.path.exists("./cookies.txt") else "Not available"
        }
        
        # Verify VPN connectivity if running in production
        if is_production:
            # Check if OpenVPN process is running
            try:
                result = subprocess.run(["pgrep", "openvpn"], capture_output=True, text=True)
                vpn_process_status = "Running" if result.stdout.strip() else "Not running"
                response["vpn_process"] = vpn_process_status
            except Exception as e:
                response["vpn_process"] = f"Error checking: {str(e)}"
            
            # Check for VPN status file that contains location information
            try:
                if os.path.exists("/tmp/vpn_status"):
                    vpn_info = {}
                    with open("/tmp/vpn_status", "r") as f:
                        for line in f:
                            if "=" in line:
                                key, value = line.strip().split("=", 1)
                                vpn_info[key] = value
                    
                    # Add VPN details to response
                    response["vpn_status"] = vpn_info
                    
                    # Log to application logs for Render (will show in Render logs)
                    if vpn_info.get("CONNECTED_TO_INDIA") == "true":
                        logger.info(f"[RENDER_VPN_STATUS] ✓ VPN connected to India: {vpn_info.get('CITY', 'Unknown')}, {vpn_info.get('REGION', 'Unknown')}")
                    else:
                        logger.warning(f"[RENDER_VPN_STATUS] ⚠ VPN not connected to India: {vpn_info.get('COUNTRY', 'Unknown')}")
                else:
                    # Try to get current IP information
                    try:
                        ip_info = requests.get('https://ipinfo.io/json', timeout=5).json()
                        response["current_ip"] = ip_info.get('ip', 'Unknown')
                        response["current_country"] = ip_info.get('country', 'Unknown')
                        response["current_region"] = ip_info.get('region', 'Unknown')
                        response["current_city"] = ip_info.get('city', 'Unknown')
                        
                        # Log to application logs for Render
                        if ip_info.get('country') == 'IN':
                            logger.info(f"[RENDER_VPN_STATUS] ✓ Connected through Indian IP: {ip_info.get('city', 'Unknown')}, {ip_info.get('region', 'Unknown')}")
                        else:
                            logger.warning(f"[RENDER_VPN_STATUS] ⚠ Not connected through Indian IP: {ip_info.get('country', 'Unknown')}")
                    except Exception as e:
                        response["ip_check_error"] = str(e)
            except Exception as e:
                response["vpn_status_error"] = str(e)
        
        # Check YouTube connectivity
        try:
            yt_response = requests.head('https://www.youtube.com', timeout=5)
            response["youtube_access"] = {
                "status": "Available" if yt_response.status_code < 400 else "Restricted",
                "status_code": yt_response.status_code
            }
        except Exception as e:
            response["youtube_access"] = {"status": "Error", "error": str(e)}
        
        return jsonify(response)
    except Exception as e:
        logger.error(f"Health check failed: {str(e)}")
        return jsonify({"status": "unhealthy", "error": str(e)}), 500

@app.errorhandler(404)
def not_found_error(error):
    return render_template('error.html', error="Page not found"), 404

@app.errorhandler(500)
def internal_error(error):
    logger.error(f"Internal server error: {str(error)}")
    return render_template('error.html', error="Internal server error"), 500

@app.after_request
def add_header(response):
    """Add headers to prevent caching for dynamic content"""
    if 'Cache-Control' not in response.headers:
        response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, post-check=0, pre-check=0, max-age=0'
        response.headers['Pragma'] = 'no-cache'
        response.headers['Expires'] = '-1'
    return response