from mlbapi import mlbapi
from pprint import pprint
import pandas as pd


# https://www.baseball-almanac.com/players/home_run.php?p=judgeaa01
def main(year):
    judgegames = []
    api = mlbapi()
    games = api.schedule(year=year, team='Yankees')
    homersSoFar=0
    for gamePk, gamedata in games.items():
        # df = api.playByPlay(662010)
        if gamedata['status']['abstractGameState'] in ['Preview']:
            continue
        df = api.playByPlay(gamePk)
        df['season'] = gamedata['season']
        df['seriesDescription'] = gamedata['seriesDescription']
        df['gameDate'] = gamedata['gameDate']
        df['officialDate'] = gamedata['officialDate']
        for attr in ['home', 'away']:
            df[f'{attr}Team'] = gamedata['teams'][attr]['team']['name']
            df[f'{attr}TeamId'] = gamedata['teams'][attr]['team']['id']
        df_judge = df[df['batterFullName'] == 'Aaron Judge']

        judgegames.append(df[df['batterFullName'] == 'Aaron Judge'])
        # print(df_judge)
    df_judge = pd.concat(judgegames, ignore_index=True)
    df_judge = df_judge[df_judge.seriesDescription == 'Regular Season']
    df_judge['homeRunCnt'] = df_judge['homeRunCnt'].ffill().fillna(0)  # forward fill games with no homers with previous total

    # print(f"all at bats ({df_judge.shape[0]})")
    # df_judge_all_pitches = df_judge.groupby('finalPitchType').size()
    # for pitch, cnt in df_judge_all_pitches.items():
    #     print(f"{pitch:20} {(cnt / df_judge.shape[0]) * 100:5.1f}%")
    #
    # df_judge_homers = df_judge[df_judge['result'] == "Home Run"]
    # print(f"\nhomer at bats ({df_judge_homers.shape[0]})")
    # df_judge_hr_pitches = df_judge_homers.groupby('finalPitchType').size()
    # for pitch, cnt in df_judge_hr_pitches.items():
    #     print(f"{pitch:20} {(cnt / df_judge_homers.shape[0]) * 100:.1f}%")
    #
    prevhrs = -1
    str = "<TABLE BORDER=1>\n"
    for i, atbat in df_judge.iterrows():
        if prevhrs != atbat['homeRunCnt']:
            prevhrs = atbat['homeRunCnt']
            str += f"\n<tr><th>{atbat['homeRunCnt']}<th>{prevhrs}"
    str += "\n</TABLE>\n"
    print(str)


if __name__ == '__main__':
    main(2022)
