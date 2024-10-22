# Torrent-app

Build a simple CLI torrent-app for P2P file sharing

## Available Commands:
    -------------------------
    - `add`                 : Publish your documents into the network
    - `delete   <code>`     : Delete your published documents
    - `ls`                  : List all your published documents 
    - `seed     <code>`     : Start sharing your documents 
    - `get      <code>`     : Start downloading documents
    - `stop     <code>`     : Stop downloading/sharing documents 
    - `show`                : Show download progress
    - `peers    <code>`     : List all peers you're connected to 
    - `scrape   <code>`     : Check the current info of the torrent network
    - `help`                : Display available commands
    - `clear`               : Clear the screen
    - `logout`              : Log out of your account
    - `exit`                : Exit the program



## Virtual environment setup and run project
Create venv
```sh
python -m venv venv
```
Active venv for window
```sh
python -m venv venv
```
Active for Linux/MacOS
```sh
source venv/bin/activate
```
Install dependencies
```sh
pip install -r requirements.txt
```
Run project 
```sh
python main.py
```


## Project structure

```py
📦src
 ┣ 📄 .env.example                  # all environment variables in program
 ┣ 📄 add_delete_ls.py              # add + delete + ls command
 ┣ 📄 auth.py                       # login + register command 
 ┣ 📄 config.py                     # Load environment variable 
 ┣ 📄 fetch_api.py                  # fetch + post + delete API function
 ┣ 📄 get_seed_peers.py             # get + seed + peers commands  
 ┣ 📄 scrape.py                     # scrape command
 ┣ 📄 show.py                       # show command 
 ┣ 📄 upload.py                     # Upload algorithm 
 ┣ 📄 download.py                   # download handler
 ┣ 📄 requirement.txt               # all libraries and version for this program  
 ┗ 📜 main.py                       # main file to run program
```
