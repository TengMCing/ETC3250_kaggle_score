#!/bin/sh
python3 kaggle_laed.py
git add .
git commit -m "Updated: `date +'%Y-%m-%d %H:%M:%S'`"
git push
