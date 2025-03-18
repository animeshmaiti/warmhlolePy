## Requirements libraries
```bash
pip install magic-wormhole twisted
```
## Run Script
```bash
python script.py send file/my_file.txt
python script.py receive <generated_code>
```
## flask server with ngrok
ngrok setup [doc](https://dashboard.ngrok.com/get-started/setup/linux)
```bash
python server.py
# Add the ngrok repository to your apt sources
curl -s https://ngrok-agent.s3.amazonaws.com/ngrok.asc | sudo tee /etc/apt/trusted.gpg.d/ngrok.asc >/dev/null
echo "deb https://ngrok-agent.s3.amazonaws.com buster main" | sudo tee /etc/apt/sources.list.d/ngrok.list
# Update your apt package database
sudo apt update && sudo apt install ngrok
ngrok config add-authtoken <your_auth_token>
ngrok http 5000
```

### Description
This script is used to send and receive files between two devices. The sender will generate a code that the receiver will use to download the file. The file will be stored in the same directory as the script.
