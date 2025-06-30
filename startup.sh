#!/bin/bash
apt update && apt install -y libgl1 libglib2.0-0
gunicorn -b 0.0.0.0:8000 app:app
