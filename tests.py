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
        result = uut.playbyplay(662062)
        pprint(result)

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

    @unittest.skip('broke')
    def test_something(self):
        uut = mlbapi()
        day = datetime(2022, 3, 1)
        current_date = datetime(2022, 5, 1)
        str = "<table>\n<TH>0</TH><TD>"
        hr = 0
        while day <= current_date:
            day += timedelta(days=1)
            atbats, links = uut.schedule(date=day)
            if len(links) < 1:
                continue
            # print(day, hr, links, gamestr)
            if 'E' in gamestr:
                hr += gamestr.count('E')
                str += f"</tr>\n<th>{hr}</th><td>"
            str += gamestr
        print(str)


if __name__ == '__main__':
    unittest.main()
