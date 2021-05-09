import requests
import os
import zipfile
import csv
import datetime


def mark(score):
    std = [0.88172, 0.861, 0.800, 0.769, 0.738, 0.667, 0.561, 0.656]
    return(15 - len([0 for _ in std if float(score) <= _]))

cwd = os.getcwd()
target_path = os.path.join(cwd, "data/publicleaderboarddata.zip")

r = requests.get("https://www.kaggle.com/c/27753/publicleaderboarddata.zip", stream = True)

with open(target_path, "wb") as f:
    for chunk in r.iter_content(chunk_size = 128):
        f.write(chunk)


with zipfile.ZipFile(target_path, 'r') as zip_ref:
    zip_ref.extractall(os.path.join(cwd, 'data'))
    csv_name = zip_ref.namelist()[0]

result = []

with open(os.path.join(cwd, 'data', csv_name), 'r') as f:
    f.readline()
    csv_reader = csv.reader(f, delimiter = ",")
    for row in csv_reader:
        tmp_mark = mark(row[-1])
        if tmp_mark <= 7:
            tmp_mark = '<=7'
        result.append(row + [tmp_mark])


with open(os.path.join(cwd, 'README.md'), 'w') as f:
    f.write("# ETC3250 Kaggle score\n\n")
    f.write('**Laste updated: {a}**\n\n'.format(a = datetime.datetime.now().strftime('%B %d, %Y %H:%M:%S')))
    f.write('## Public leaderboard\n\n')
    f.write('|Team Id|Team Name|Submission Date|Score|Points|\n')
    f.write('|---|---|---|---|---|\n')
    for row in result:
        f.write('|' + '|'.join([str(_) for _ in row]) + '|\n')

