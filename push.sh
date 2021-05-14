#!/bin/sh
python kaggle_laed.py
git add .
git commit -m "`date +\"%Y-%m-%d\"`"
git push
