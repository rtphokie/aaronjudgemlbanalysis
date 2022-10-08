from mlbapi import mlbapi
import pandas as pd
from tqdm import tqdm

# data source MLB official API: http://statsapi.mlb.com
# additional validation from https://www.baseball-almanac.com/players/home_run.php?p=judgeaa01


def metrics(df_judge):
    pitches={}
    print(f"all at bats ({df_judge.shape[0]})")
    df_judge_all_pitches = df_judge.groupby('finalPitchType').size()
    for pitch, cnt in df_judge_all_pitches.items():
        print(f"{pitch:20} {cnt:5.1f}")
        pitches[pitch]=cnt


    df_judge_homers = df_judge[df_judge['result'] == "Home Run"]
    print(f"\nhomer at bats ({df_judge_homers.shape[0]})")
    df_judge_hr_pitches = df_judge_homers.groupby('finalPitchType').size()
    for pitch, cnt in df_judge_hr_pitches.items():
        print(f"{pitch:20} {cnt:.1f} {cnt/pitches[pitch]:f}")

    df_judge_walks = df_judge[df_judge['result'] == "Intent Walk"]
    print(f"\nIntentional Walks ({df_judge_walks.shape[0]})")
    df_judge_walks_pitchers = df_judge_walks.groupby('pitcherFullName').size()
    for pitch, cnt in df_judge_walks_pitchers.items():
        print(f"{pitch:20} {cnt:.1f}")

    df_judge_homers = df_judge[df_judge['result'] == "Home Run"]
    print(f"\npitchers ({df_judge_homers.shape[0]})")
    df_judge_hr_pitches = df_judge_homers.groupby('pitcherFullName').size()
    for pitch, cnt in df_judge_hr_pitches.items():
        print(f"{pitch:20} {cnt:.0f}")

    df_judge_homers = df_judge[df_judge['result'] == "Home Run"]
    print(f"\nopponents ({df_judge_homers.shape[0]})")
    df_judge_hr_pitches = df_judge_homers.groupby('opponentTeam').size()
    for pitch, cnt in df_judge_hr_pitches.items():
        print(f"{pitch:20} {cnt:.0f}")

    df_judge_homers = df_judge[df_judge['result'] == "Home Run"]
    print(f"\nvenues ({df_judge_homers.shape[0]})")
    df_judge_hr_pitches = df_judge_homers.groupby('venue').size()
    for pitch, cnt in df_judge_hr_pitches.items():
        print(f"{pitch:20} {cnt:.0f}")


    print(f"\nIntentional Walks")
    df_intentional=df_judge[df_judge['result'] == "Intent Walk"]
    print(df_intentional[['calls', 'pitcherFullName', 'officialDate']])

    print("\n Eephus pitches")
    df_eephus = df_judge[df_judge['finalPitchType'] == 'Eephus']
    print(df_eephus)

def main(year):
    judgegames = []
    api = mlbapi()
    games = api.schedule(year=year, team='New York Yankees')
    for gamePk, gamedata in games.items():
        if gamedata['status']['abstractGameState'] in ['Preview'] or gamedata['status']['detailedState'] in [
            'Postponed', 'Cancelled']:
            continue
        df = api.playByPlay(gamePk)
        df['season'] = gamedata['season']
        df['venue'] = gamedata['venue']['name']
        df['seriesDescription'] = gamedata['seriesDescription']
        df['gameDate'] = gamedata['gameDate']
        df['officialDate'] = gamedata['officialDate']
        for attr in ['home', 'away']:
            df[f'{attr}Team'] = gamedata['teams'][attr]['team']['name']
            df[f'{attr}TeamId'] = gamedata['teams'][attr]['team']['id']
        if gamedata['teams']['home']['team']['name'] == 'New York Yankees':
            df[f'opponentTeam']=gamedata['teams']['away']['team']['name']
        else:
            df[f'opponentTeam']=gamedata['teams']['home']['team']['name']
        judgegames.append(df[df['batterFullName'] == 'Aaron Judge'])
    df_judge = pd.concat(judgegames, ignore_index=True)
    df_judge = df_judge[df_judge.seriesDescription == 'Regular Season']
    df_judge['homeRunCnt'] = df_judge['homeRunCnt'].ffill().fillna(
        0)  # forward fill games with no homers with previous total
    return df_judge


def htmltable(df_judge):
    api = mlbapi()

    callcolor = {'*B': {'code': '*B', 'description': 'Ball In Dirt', 'color': 'blue'},
                 'B': {'code': 'B', 'description': 'Ball', 'color': 'blue'},
                 'H': {'code': 'H', 'description': 'Hit By Pitch', 'color': 'blue'},
                 'C': {'code': 'C', 'description': 'Called Strike', 'color': 'orange'},
                 'S': {'code': 'S', 'description': 'Swinging Strike', 'color': 'orange'},
                 'W': {'code': 'W', 'description': 'Swinging Strike (Blocked)', 'color': 'orange'},
                 'D': {'code': 'D', 'description': 'In play, no out', 'color': '#33FF4C'},
                 'E': {'code': 'E', 'description': 'In play, run(s)', 'color': 'green'},
                 'F': {'code': 'F', 'description': 'Foul', 'color': 'grey'},
                 'L': {'code': 'L', 'description': 'Foul Bunt', 'color': 'grey'},
                 'M': {'code': 'M', 'description': 'Missed Bunt', 'color': 'orange'},
                 'O': {'code': 'O', 'description': 'Foul Tip', 'color': 'grey'},
                 'P': {'code': 'P', 'description': 'Pitchout', 'color': 'blue'},
                 'T': {'code': 'T', 'description': 'Foul Tip', 'color': 'grey'},
                 'V': {'code': 'V', 'description': 'Automatic Ball', 'color': 'blue'},
                 'X': {'code': 'X', 'description': 'In play, out(s)', 'color': 'red'}}

    resultmap = {
        'Single': {'code': 'S', 'color': 'green', 'simple': 'single'},
        'Double': {'code': 'D', 'color': 'green', 'simple': 'double'},
        'Triple': {'code': 'T', 'color': 'green', 'simple': 'triple'},
        'Field Error': {'code': 'S', 'color': 'green', 'simple': 'single'},
        'Fielders Choice': {'code': 'S', 'color': 'green', 'simple': 'single'},
        'Home Run': {'code': 'H', 'color': 'green', 'simple': 'home run'},
        'Sac Fly': {'code': 'X', 'color': 'green', 'simple': 'sac fly'},
        'Forceout': {'code': 'X', 'color': '#EA9FA2', 'simple': 'out'},
        'Strikeout': {'code': 'X', 'color': 'red', 'simple': 'out'},
        'Lineout': {'code': 'X', 'color': 'red', 'simple': 'out'},
        'Double Play': {'code': 'X', 'color': 'red', 'simple': 'out'},
        'Grounded Into DP': {'code': 'X', 'color': 'red', 'simple': 'out'},
        'Groundout': {'code': 'X', 'color': 'red', 'simple': 'out'},
        'Pop Out': {'code': 'X', 'color': 'red', 'simple': 'out'},
        'Flyout': {'code': 'X', 'color': 'red', 'simple': 'out'},
        'Walk': {'code': 'W', 'color': 'blue', 'simple': 'walk'},
        'Hit By Pitch': {'code': 'W', 'color': 'blue', 'simple': 'walk'},
        'Intent Walk': {'code': 'w', 'color': '#FF00E0', 'simple': 'intentional walk'},
        'Catcher Interference': {'code': 'W', 'color': 'blue', 'simple': 'walk'},
    }

    legend = {}
    fp = open('judge.html', 'w')
    fp.writelines('')
    fp.close()
    homerdatestotal={}
    homerdates={}
    for i, atbat in tqdm(df_judge.iterrows()):
        if resultmap[atbat['result']]['code'] == 'H':
            if atbat['officialDate'] not in homerdates.keys():
                homerdates[atbat['officialDate']]=0
                homerdatestotal[atbat['officialDate']]=0
            homerdatestotal[atbat['officialDate']]+=1
    # df_judge = df_judge.iloc[::-1]

    str = "<TABLE BORDER=0 style=\"font-family: Arial, sans-serif;\"><TR>"
    for i in range(100):
        str += f'<td>{"&nbsp;"*10}</td>'
    str += "</tr>\n"

    str+="<tr><th>1</th><td>"
    rowcnt=1
    prevdate=None
    descs=[]
    for i, atbat in df_judge.iterrows():
        str += f"<span style=\"color: {resultmap[atbat['result']]['color']}\">{resultmap[atbat['result']]['code']}</span>"
        # if prevdate is not None and prevdate != atbat['gameDate']:
        #     str+='|'
        # prevdate=atbat['gameDate']
        if resultmap[atbat['result']]['code'] == 'H':
            descs.append(atbat['pitcherFullName'])
            homerdates[atbat['officialDate']] += 1
            if homerdates[atbat['officialDate']] ==  homerdatestotal[atbat['officialDate']]:
                str+=f"</td><td colspan=26>"
                str+=" off "
                str+=" & ".join(descs)
                str+=f" {api.teams_byname[atbat['awayTeam']]['abbreviation']}"
                str+=f" at {api.teams_byname[atbat['homeTeam']]['abbreviation']}"
                if homerdatestotal[atbat['officialDate']] > 1 and len(descs) == 1:
                    str+=f" ({homerdatestotal[atbat['officialDate']]} homers)"
                descs=[]
                str+=f" {atbat['officialDate']}"
                str+=f"</td></tr>\n"
                str+=f"<tr><th>{atbat['homeRunCnt']+1:.0f}</th>"
                for x in range(rowcnt):
                    str += f"<th>&nbsp;</th>\n"
                str+="<td>"
                rowcnt+=1

    str += "</TR>\n</TABLE>\n"


    print('done')

    str += "<TABLE BORDER=0 style=\"font-family: Arial, sans-serif;\"><TR>"
    for k, v in legend.items():
        str += f"<TR><TH>{k}</TH><TD>{v}</TD></TR>\n"

    str += "</TABLE>\n"
    fp = open('judge.html', 'w')
    fp.writelines(str)
    fp.close()
    # pprint(api.calldesc)


if __name__ == '__main__':
    df_judge = main(2022)
    print(df_judge)
    metrics(df_judge)
    # htmltable(df_judge)
