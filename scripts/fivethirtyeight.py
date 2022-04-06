
import pandas as pd
import datetime

def soccer():
   
   # reading the .csv directly from their site 
   url = "https://projects.fivethirtyeight.com/soccer-api/club/spi_matches_latest.csv"
   five_soccer = pd.read_csv(url)

   # filtering to premier league games
   premier_league = five_soccer[five_soccer['league'] == 'Barclays Premier League']

   # extracting just games today and beyond
   curr_date = pd.to_datetime(datetime.datetime.now().date())
   tomorrow = curr_date + datetime.timedelta(days=1)
   premier_league['date'] = premier_league.loc[:,'date'].map(pd.to_datetime)
   premier_league = premier_league[premier_league['date'].isin([curr_date, tomorrow])]

   premier_league = premier_league[premier_league['date'] >= curr_date]

   # subsetting columns
   premier_league = premier_league[['date', 'league', 'team1', 'team2', 'prob1', 'prob2', 'probtie']]

   # elongating the data
   team_one = premier_league.drop(columns=['prob2', 'probtie'])
   team_one['bet_side'] = team_one.loc[:,'team1']
   team_one = team_one.rename(columns={
      'prob1': 'win_prob'
   })  

   team_two = premier_league.drop(columns=['prob1', 'probtie'])
   team_two['bet_side'] = team_two.loc[:,'team2']
   team_two = team_two.rename(columns={
      'prob2': 'win_prob'
   })  

   team_tie = premier_league.drop(columns=['prob1', 'prob2'])
   team_tie['bet_side'] = 'Draw'
   team_tie = team_tie.rename(columns={
      'probtie': 'win_prob'
   })  

   # joining the data and reindexing
   soccer_long = pd.concat([team_one, team_two, team_tie])
   soccer_long = soccer_long[['date', 'league', 'team1', 'team2', 'bet_side', 'win_prob']]

   # doing some team name cleaning that will make it easier to join our data
   soccer_lookup = pd.read_csv("lookups/soccer_team_lookup.csv")
   soccer_long = soccer_long.merge(soccer_lookup, left_on='bet_side', right_on='fivethirtyeight')
   soccer_long['bet_side'] = soccer_long.loc[:,'odds']
   soccer_long['league'] = 'EPL'
   soccer_long = soccer_long.drop(columns=['fivethirtyeight', 'odds'])
   
   soccer_long = soccer_long.sort_values(by=['date', 'team1'])
   soccer_long = soccer_long.reset_index(drop=True)

   return soccer_long

# gets the current nba forecast
def basketball():
   
   # reading the .csv directly from their site 
   url = "https://projects.fivethirtyeight.com/nba-model/nba_elo_latest.csv"
   five_nba = pd.read_csv(url)

   # subsetting only the important columns
   columns = ['date', 'team1', 'team2', 'raptor_prob1', 'raptor_prob2']
   five_nba = five_nba[columns]

   # fixing dates quickly
   five_nba['date'] = pd.to_datetime(five_nba.loc[:,'date'])

   # getting the next two days of games
   curr_date = datetime.datetime.now().date()
   tomorrow = curr_date + datetime.timedelta(days=1)
   five_nba = five_nba[five_nba['date'].isin([curr_date, tomorrow])]

   # elongating the data
   team_one = five_nba.drop(columns=['raptor_prob2'])
   team_one['bet_side'] = team_one.loc[:,'team1']
   team_one = team_one.rename(columns={
      'raptor_prob1': 'win_prob'
   })

   team_two = five_nba.drop(columns=['raptor_prob1'])
   team_two['bet_side'] = team_two.loc[:,'team2']
   team_two = team_two.rename(columns={
      'raptor_prob2': 'win_prob'
   })

   # joining the data, sorting + reindexing
   nba_long = pd.concat([team_one, team_two])
   nba_long['league'] = 'NBA'
   nba_long['win_prob'] = nba_long.loc[:,'win_prob'].map(lambda x: round(x, 4))
   
   # cleaning up the bet side team names
   name_lookup = pd.read_csv("lookups/nba_lookup.csv", index_col=0)
   nba_long = nba_long.merge(name_lookup, left_on=["bet_side"], right_on=["team_abrv"])
   nba_long['bet_side'] = nba_long.loc[:,'team_name']

   nba_long = nba_long.drop(columns=['team_name', 'team_abrv'])

   nba_long = nba_long.sort_values(by=['date', 'team1'])
   nba_long = nba_long.reset_index(drop=True)

   return nba_long

def hockey():
   # reading the .csv directly from their site 
   url = "https://projects.fivethirtyeight.com/nhl-api/nhl_elo_latest.csv"
   five_nhl = pd.read_csv(url)

   # subsetting columns
   columns = ['date', 'home_team', 'away_team', 'home_team_winprob', 'away_team_winprob']
   five_nhl = five_nhl[columns]

   # cleaning up dates and getting only games from today and tomorrow
   five_nhl['date'] = pd.to_datetime(five_nhl.loc[:,'date'])

   curr_date = datetime.datetime.now().date()
   tomorrow = curr_date + datetime.timedelta(days=1)
   five_nhl = five_nhl[five_nhl['date'].isin([curr_date, tomorrow])]

   home_team = five_nhl.drop(columns=['away_team_winprob'])
   home_team['bet_side'] = home_team.loc[:,'home_team']
   home_team = home_team.rename(columns={
      'home_team': 'team1',
      'away_team': 'team2',
      'home_team_winprob': 'win_prob'
   })

   away_team = five_nhl.drop(columns=['home_team_winprob'])
   away_team['bet_side'] = away_team.loc[:,'away_team']
   away_team = away_team.rename(columns={
      'home_team': 'team1',
      'away_team': 'team2',
      'away_team_winprob': 'win_prob'
   })

   nhl_long = pd.concat([home_team, away_team])
   nhl_long['win_prob'] = nhl_long.loc[:,'win_prob'].map(lambda x: round(x, 4))
   nhl_long['league'] = 'NHL'

   nhl_long = nhl_long.reset_index(drop=True)

   return nhl_long

# main scripting function
def get_fivethirtyeight():
   nba_long = basketball()
   soccer_long = soccer()
   nhl_long = hockey()

   sports_long = pd.concat([soccer_long, nba_long, nhl_long])
   sports_long['win_prob'] = sports_long['win_prob'].map(lambda x: round(x, 3))
   sports_long.to_csv("../forecasts_today.csv")

   return sports_long

get_fivethirtyeight()