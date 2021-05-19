#!/bin/sh
open down.html
sleep 5
mv ~/Downloads/spotoroo-publicleaderboard.zip ./data/spotoroo-publicleaderboard.zip
git log --follow --reverse -p data/spotoroo-publicleaderboard.csv > data/log.txt
python3 kaggle_lead.py
rm data/log.txt
git add .
git commit -m "Updated: `date +'%Y-%m-%d %H:%M:%S'`"
git push
