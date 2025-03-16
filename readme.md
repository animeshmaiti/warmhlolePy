## Requirements libraries
```bash
pip install magic-wormhole twisted
```
## Run Script
```bash
python script.py send file/my_file.txt
python script.py receive <generated_code>
```
### Description
This script is used to send and receive files between two devices. The sender will generate a code that the receiver will use to download the file. The file will be stored in the same directory as the script.
