# Torrent-app

Build a simple CLI torrent-app for P2P file sharing 

## Run project 
```sh
python main.py
```

## Virtual environment setup
### Create venv
```sh
python -m venv venv
```
### Active for window
```sh
python -m venv venv
```
### Active for Linux/MacOS
```sh
source venv/bin/activate
```
### Install dependencies
```sh
pip install -r requirements.txt
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
