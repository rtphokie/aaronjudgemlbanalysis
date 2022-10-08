import pandas as pd
import re
from datetime import datetime, timedelta
import requests_cache
from pprint import pprint
import pandas as pd

pd.set_option('display.max_columns', None)
pd.set_option('display.max_rows', None)
pd.set_option('display.width', None)
current_date = datetime.now()


# https://github.com/toddrob99/MLB-StatsAPI/blob/master/statsapi/endpoints.py

class mlbapi(object):
    calldesc = {}

    def __init__(self):
        self.base = 'http://statsapi.mlb.com'
        self.sportid = 1
        self.session_cached = requests_cache.CachedSession('mlbapicache', expire_after=86000)
        self.teams_byname, self.teams_byid, self.teams_bycode = self.teams()

    def teams(self, sportId=1):
        # team names short and long, abbreviations tc.
        url = f"{self.base}/api/v1/teams?sportId={sportId}"
        r = self.session_cached.get(url)
        data = r.json()
        byname = {}
        byid = {}
        bycode = {}
        for teamdata in data['teams']:
            byname[teamdata['name']] = teamdata
            byid[teamdata['id']] = teamdata
            bycode[teamdata['fileCode']] = teamdata
        return byname, byid, bycode

    def schedule(self, team=None, date=None, year=2022):
        if team is not None:
            try:
                teamId = self.teams_byname[team]['id']
            except:
                teamId = ''
        if date is None:
            startDate = f"{year}-01-01"
            endDate = f"{year}-12-31"
            datestr = ''
        else:
            datestr = date.isoformat()[:10]
            startDate = ''
            endDate = ''

        url = f"{self.base}/api/v1/schedule/games/?sportId=1&date={datestr}&startDate={startDate}&endDate={endDate}&teamId={teamId}"
        r = self.session_cached.get(url)
        data = r.json()
        result = {}
        for datedata in data['dates']:
            for gamedata in datedata['games']:
                result[gamedata['gamePk']] = gamedata
        return result

    def playByPlay(self, gamePk):
        url = f"{self.base}/api/v1/game/{gamePk}/playByPlay"
        r = self.session_cached.get(url)
        data = r.json()

        rows=[]
        row={}
        prevatBatIndex=-1
        pitchcount={}
        for playdata in data['allPlays']:
            if prevatBatIndex != playdata['about']['atBatIndex']:
                if prevatBatIndex >= 0:
                    rows.append(row)
                row={'result': playdata['result']['event'], 'description': playdata['result']['description'],
                     'rbi': playdata['result']['rbi'], 'calls': [],
                     'count': playdata['count'].values(),
                     'finalPitchType': None,
                     'gamePk': gamePk,
                     'homeRunCnt': None,
                     'inning': playdata['about']['inning'],
                     'halfInning': playdata['about']['halfInning'],
                     'startTime': playdata['about']['startTime'],
                     'endTime': None,
                     'finalPitchSpeed': None,
                     'pitchCount': None,
                     'batterId': playdata['matchup']['batter']['id'], 'batterFullName': playdata['matchup']['batter']['fullName'],
                     'pitcherId': playdata['matchup']['pitcher']['id'], 'pitcherFullName': playdata['matchup']['pitcher']['fullName']}
                desccntmatch= re.search("[homersi|hits a grand slam] \((\d+)\)", playdata['result']['description'])
                if desccntmatch and row['result'] == 'Home Run':
                    row['homeRunCnt']=int(desccntmatch.group(1))

            for playevent in playdata['playEvents']:
                if playevent['isPitch']:
                    row['calls'].append(playevent['details']['code'].replace('*', ''))
                    if playevent['details']['code'] not in self.calldesc.keys():
                        self.calldesc[playevent['details']['code']]=playevent['details']['call']

                    if 'type' in playevent['details']:
                        row['finalPitchType']=playevent['details']['type']['description']
                    if 'endSpeed' in playevent['pitchData']:
                        row['finalPitchSpeed']=playevent['pitchData']['endSpeed']
                    row['finalCount']=playevent['count'].values()
                    row['endTime']=playdata['about']['endTime']
                    if playdata['matchup']['pitcher']['id'] not in pitchcount.keys():
                        pitchcount[playdata['matchup']['pitcher']['id']]=0
                    pitchcount[playdata['matchup']['pitcher']['id']]+=1
                    row['pitchCount']=pitchcount[playdata['matchup']['pitcher']['id']]

                prevatBatIndex=playdata['about']['atBatIndex']
        rows.append(row)
        df=pd.DataFrame.from_records(rows)
        return df

    def players(self, firstName=None, lastName=None, currentTeam=None):
        url = f"{self.base}/api/v1/sports/1/players"
        r = self.session_cached.get(url)
        data = r.json()
        results = {}
        for player in data['people']:
            if firstName is None or firstName == player['firstName']:
                if lastName is None or lastName == player['lastName']:
                    if currentTeam is None or currentTeam == player['currentTeam']:
                        results[player['id']] = player
        return results

    def live(self, endpoint):
        url = f"{self.base}/{endpoint}"
        r = self.session_cached.get(url)
        data = r.json()
        call = []
        atbats = []
        hrs = 0
        for play in data['liveData']['plays']['allPlays']:
            if play['matchup']['batter']['id'] == 592450:
                # print(play['matchup']['batter']['fullName'], play['about']['startTime'])
                result = {'result': None, 'events': [], 'rbi': None}
                for event in play['playEvents']:
                    if event['isPitch']:
                        result['events'].append(event['details']['call']['code'])
                        # print(event['details']['call']['code'])
                result['result'] = play['result']['event']
                result['rbi'] = play['result']['rbi']
                print(play['result']['event'])
                atbats.append(result)
        return atbats, hrs
