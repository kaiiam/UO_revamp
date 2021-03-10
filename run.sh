#!/usr/bin/env nix-shell
#!nix-shell -i bash -p bash python38Full
trap 'exit 0' 1 2 15
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
pip install -e .
export FLASK_APP=server/server.py
export FLASK_ENV=development
export FLASK_DEBUG=1
flask run --port ${PORT:=5000}
