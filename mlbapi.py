import pandas as pd
from datetime import datetime, timedelta
import requests_cache
from pprint import pprint

pd.set_option('display.max_columns', None)
current_date = datetime.now()


# https://github.com/toddrob99/MLB-StatsAPI/blob/master/statsapi/endpoints.py

class mlbapi(object):

    def __init__(self):
        self.base = 'http://statsapi.mlb.com'
        self.sportid = 1
        self.session_cached = requests_cache.CachedSession('mlbapicache', expire_after=86000)
        self.teams_byname, self.teams_byid, self.teams_bycode = self.teams()

    def teams(self, sportId=1):
        url = f"{self.base}/api/v1/teams?sportId={sportId}"
        r = self.session_cached.get(url)
        data = r.json()
        byname = {}
        byid = {}
        bycode = {}
        for teamdata in data['teams']:
            byname[teamdata['clubName']] = teamdata
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
        # print(date.isoformat()[:10])
        result = {}
        for datedata in data['dates']:
            for gamedata in datedata['games']:
                result[gamedata['gamePk']] = gamedata
        return result

        #         if 'Yankees' in game['teams']['away']['team']['name'] or 'Yankees' in game['teams']['home']['team'][
        #             'name']:
        #             # print(f"{game['teams']['away']['team']['name']} {game['teams']['home']['team']['name']}")
        #             str = ''
        #             atbats = self.live(game['link'])
        #             links.append(game['link'])
        #             for atbat in atbats:
        #                 for event in atbat['events']:
        #                     str += event.replace('*', '')
        #                 str += '-'
        #             strs.append(str)
        # return strs, links

    def playbyplay(self, gamePk):
        url = f"http://statsapi.mlb.com/api/v1/game/{gamePk}/playByPlay"
        r = self.session_cached.get(url)
        data = r.json()
        result={}
        for playdata in data['allPlays']:
            play={}
            result[playdata[]]=play
        return data

    def players(self, firstName=None, lastName=None, currentTeam=None):
        url = f"http://statsapi.mlb.com/api/v1/sports/1/players"
        r = self.session_cached.get(url)
        data = r.json()
        results = {}
        for player in data['people']:
            if firstName is None or firstName == player['firstName']:
                if lastName is None or lastName == player['lastName']:
                    if currentTeam is None or currentTeam == player['currentTeam']:
                        results[player['id']]=player
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

