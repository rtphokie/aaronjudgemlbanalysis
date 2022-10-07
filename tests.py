import unittest
from pprint import pprint
from mlbapi import mlbapi

class MyTestCase(unittest.TestCase):
    def test_team(self):
        uut = mlbapi()
        byname, byid, bycode = uut.teams()
        self.assertEqual(len(byname), 30)
        self.assertEqual(len(byname), len(byid))
        self.assertEqual(len(byid), len(bycode))

    def test_playbyplay(self):
        uut = mlbapi()
        # df = uut.playByPlay(662010) # 62
        df = uut.playByPlay(661301) # 10
        print(df[df['result'] == 'Home Run'])
        print(df)
        # result = uut.playByPlay(706889)
        # ts=list(result.keys())
        # # pprint(result[ts[0]])

    def test_players(self):
        uut = mlbapi()
        result = uut.players()
        self.assertGreaterEqual(len(result), 1500)
        result = uut.players(firstName='Aaron', lastName='Judge')
        self.assertGreaterEqual(len(result), 1)

    def test_season(self):
        uut = mlbapi()
        result = uut.schedule(year=2022, team='Yankees')
        self.assertGreaterEqual(len(result), 180)
        for gamePk, data in result.items():
            print(gamePk, data['gameDate'])
        # pprint(result)


if __name__ == '__main__':
    unittest.main()
