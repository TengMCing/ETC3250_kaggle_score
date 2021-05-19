import requests
import os
import zipfile
import csv
import datetime
from pytz import timezone
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import collections
import seaborn as sns
from statistics import median


def mark(score):
    std = [0.88172, 0.861, 0.800, 0.769, 0.738, 0.677, 0.661, 0.656]
    return(15 - len([0 for _ in std if float(score) <= _]))

def handle_his():
    cwd = os.getcwd()
    with open(os.path.join(cwd, "data", "log.txt"), 'r') as f:
        file_hist = []
        current_dist = {}
        start = False
        plus = False
        for line in f:

            if 'commit' in line:
                if start == True:
                    start = False
                    file_hist.append(current_dist)
                    current_dist = {}
                    continue

            if "Date:" in line:
                line = line.replace(' '*3, ' ').replace(' '*2, ' ')
                current_dist['date'] = line.split(' ')[2:6]
                current_dist['date'][3] = current_dist['date'][3].zfill(2)
                current_dist['date'] = ' '.join(current_dist['date'])
                current_dist['date'] = datetime.datetime.strptime(
                    current_dist['date'],
                    '%b %d %H:%M:%S %Y')
                current_dist['score'] = []
                current_dist['plus'] = []
                current_dist['team_id'] = []
                continue

            if '@@' in line:
                start = True
                continue

            if start:
                if '+' == line[0] or '-' == line[0]:
                    plus = True if '+' == line[0] else False
                    line = line[1:]
                    team_name = line.replace('\n', '').split(',')[1]
                    team_id = line.replace('\n', '').split(',')[0]

                    if team_name == 'Admin' or team_name == 'Admin2':
                        continue

                    try:
                        if float(line.replace('\n', '').split(',')[-1]) >= 1:
                            continue
                    except:
                        pass

                    score = line.replace('\n', '').split(',')[-1]
                    try:
                        score = float(score)
                        team_id = int(team_id)
                        current_dist['score'].append(score)
                        current_dist['plus'].append(plus)
                        current_dist['team_id'].append(team_id)
                    except:
                        pass

        file_hist.append(current_dist)

        file_stat = []

        current_sum_score = 0
        current_sum_point = 0
        all_team_id = []

        for commit in file_hist:
            current_dist = {}
            current_dist['date'] = commit['date']
            for x, y in zip(commit['score'], commit['plus']):
                if y:
                    current_sum_score += x
                    current_sum_point += mark(x)
                else:
                    current_sum_score -= x
                    current_sum_point -= mark(x)
            all_team_id = all_team_id + commit['team_id']
            total_number = len(collections.Counter(all_team_id).keys())
            current_dist['mean_score'] = current_sum_score/total_number
            current_dist['mean_point'] = current_sum_point/total_number
            current_dist['total_number'] = total_number
            file_stat.append(current_dist)

        plt.clf()
        fig, axs = plt.subplots(2, sharex=True)
        fig.suptitle('Mean scores and mean points')
        axs[0].plot([_['date'] for _ in file_stat],
            [_['mean_score'] for _ in file_stat],
            '-bo',
            markersize = 3,
            mfc= 'red',
            mec = 'k')
        axs[1].plot([_['date'] for _ in file_stat],
            [_['mean_point'] for _ in file_stat],
            '-bo',
            markersize = 3,
            mfc= 'red',
            mec = 'k')
        axs[1].xaxis.set_major_formatter(mdates.DateFormatter('%b %d'))
        plt.savefig(os.path.join(cwd, "data/timeline.png"), dpi = 300)















cwd = os.getcwd()
target_path = os.path.join(cwd, "data/spotoroo-publicleaderboard.zip")

# r = requests.get("https://www.kaggle.com/c/27753/publicleaderboarddata.zip", stream = True)

# with open(target_path, "wb") as f:
#     for chunk in r.iter_content(chunk_size = 128):
#         f.write(chunk)


with zipfile.ZipFile(target_path, 'r') as zip_ref:
    zip_ref.extractall(os.path.join(cwd, 'data'))
    csv_name = zip_ref.namelist()[0]

result = []

with open(os.path.join(cwd, 'data', csv_name), 'r') as f:
    f.readline()
    csv_reader = csv.reader(f, delimiter = ",")
    for row in csv_reader:
        if row[1] == "Admin":
            continue
        if row[1] == "Admin2":
            continue
        if float(row[-1]) >= 1:
            continue
        tmp_mark = mark(row[-1])
        if tmp_mark <= 7:
            tmp_mark = '<=7'

        tmp_date = datetime.datetime.strptime(
            row[2], '%Y-%m-%d %H:%M:%S'
            ).replace(
            tzinfo = datetime.timezone.utc
            ).astimezone(
            timezone("Australia/Victoria")
            ).strftime(
            '%d %b %H:%M:%S'
            )

        row[2] = tmp_date
        result.append(row + [tmp_mark])


labels = collections.Counter([mark(_[3]) for _ in result]).keys()
counts = collections.Counter([mark(_[3]) for _ in result]).values()
plt.style.use('ggplot')
plt.bar(labels, counts, align = 'center')
plt.gca().set_xticks(range(6,16))
plt.xlabel('Points')
plt.ylabel('Count')
plt.title(r'Histogram of Points, $\quad \overline{x}=' +
    str(round(sum([mark(_[3]) for _ in result])/len(result), 2)) +
    '$' +
    r', $\quad \mathrm{Median} =' +
    str(median([mark(_[3]) for _ in result])) +
    '$')
plt.savefig(os.path.join(cwd, "data/points_hist.png"), dpi = 300)


plt.clf()
plt.vlines([0.61516, 0.88172],
    ymin = 0,
    ymax = 15,
    linestyles = "dashed",
    colors = "red")
plt.annotate("Baseline", (0.61516, 15), ha = "center")
plt.annotate("Admin", (0.88172, 15), ha = "center")
sns.distplot([float(_[3]) for _ in result],
    kde = True,
    kde_kws = {'bw_adjust' : 0.5},
    color = 'darkblue',
    rug = True,
    hist = False,
    norm_hist = True)
plt.xlabel('Score')
plt.title(r'Density of Score, $\quad \overline{x}=' +
    str(round(sum([float(_[3]) for _ in result])/len(result), 4)) +
    '$' +
    r', $\quad \mathrm{Median} =' +
    str(round(median([float(_[3]) for _ in result]), 4)) +
    '$')
plt.savefig(os.path.join(cwd, "data/score_density.png"), dpi = 300)


plt.clf()
plt.hlines(range(7, 16),
    xmin = [0.88172, 0.861, 0.800, 0.769, 0.738, 0.677, 0.661, 0.656, 0][::-1],
    xmax=[1, 0.88172, 0.861, 0.800, 0.769, 0.738, 0.677, 0.661, 0.656][::-1],
    colors = "blue")
plt.vlines([0.88172, 0.861, 0.800, 0.769, 0.738, 0.677, 0.661, 0.656][::-1],
    ymin = 7,
    ymax = range(8,16),
    linestyles = 'dashed',
    colors = "blue")


j = 7
for i in [0.88172, 0.861, 0.800, 0.769, 0.738, 0.677, 0.661, 0.656][::-1]:
    j += 1
    plt.annotate(i, (i, j), ha = "center")
plt.ylim(7, 16)
plt.xlim(0.6, 1)
plt.title("Grading")
plt.xlabel("Score")
plt.ylabel("Points")
plt.savefig(os.path.join(cwd, "data/grading.png"), dpi = 300)

handle_his()


with open(os.path.join(cwd, 'README.md'), 'w') as f:
    f.write("# ETC3250 Kaggle score\n\n")
    f.write('**Last updated: {a}**\n\n'.format(a = datetime.datetime.now().strftime('%B %d, %Y %H:%M:%S')))
    f.write("## WARNING: Your final grade is based on your score on the `private leaderboard`. \n\n")
    f.write('## But the `public leaderboard` could give you some hints about your model performance.\n\n')
    f.write('## Public leaderboard\n\n')
    f.write('Number of teams: {a}\n\n'.format(a = len(result)))
    f.write('<img src="data/grading.png" width="100%" height="100%" />\n\n')
    f.write('<img src="data/score_density.png" width="100%" height="100%" />\n\n')
    f.write('<img src="data/points_hist.png" width="100%" height="100%" />\n\n')
    f.write('<img src="data/timeline.png" width="100%" height="100%" />\n\n')
    f.write('|#|Team Id|Team Name|Submission Date|Score|Points|\n')
    f.write('|---|---|---|---|---|---|\n')
    j = 0
    for row in result:
        j = j + 1
        f.write('|' + str(j) + '|' + '|'.join([str(_) for _ in row]) + '|\n')

