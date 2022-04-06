# loading packages
import pandas as pd
import datetime
import requests

# given a moneyline, calculates the implied line
def get_impl_prob(line):

   if line > 0:
      return round(100/(line+100), 3)
   elif line < 0:
      return round(abs(line)/(abs(line)+100), 3)

# given a moneyline, calculates the payout per dollar
def get_payout(line):

   if line > 0:
      return round(line / 100, 2)
   else:
      return round(100 / abs(line), 2)

# uses an API to return a json representation of the day's NBA lines
def request_moneylines(sport_key):

   # some parameters for our API request
   request_params = {
      'api_key': "920cc00f047a8d5691bfc15e1d42cd59",
      'regions': 'us',
      'markets': 'h2h',
      'oddsFormat': 'american',
      'dateFormat': 'iso',
   }

   # making our API request
   line_response = requests.get('https://api.the-odds-api.com/v4/sports/' + sport_key + '/odds', params=request_params)

   # error handling
   if line_response.status_code != 200:
      print(f'Failed to get line: status_code {line_response.status_code}, response body {line_response.text}')

   # if request successful
   else:

      # reading in response as json, restructuring to DataFrame
      lines_json = line_response.json()

      # check the usage quota
      print('Remaining requests:', line_response.headers['x-requests-remaining'])
      print('Used requests:', line_response.headers['x-requests-used'])
      return lines_json

# 
def handle_game(game_json):
   
   # 
   game_id = game_json['id']
   sport = game_json['sport_title']
   home_team = game_json['home_team']
   away_team = game_json['away_team']
   game_time = game_json['commence_time']

   bookmaker_name_list = []
   last_update_time_list = []
   bet_side_list = []
   money_line_list = []

   for bookmaker in game_json['bookmakers']:
      
      bookmaker_name = bookmaker['title']
      last_update_time = bookmaker['last_update']

      for market in bookmaker['markets']:

         for outcome in market['outcomes']:
            bet_side = outcome['name']
            money_line = outcome['price']

            bookmaker_name_list.append(bookmaker_name)
            last_update_time_list.append(last_update_time)
            bet_side_list.append(bet_side)
            money_line_list.append(money_line)

   # storing our data in a dictionary
   game_dict = {
      'game_id': game_id,
      'sport': sport,
      'date': '',
      'game_time': game_time,
      'home_team': home_team,
      'away_team': away_team,
      'bookmaker_name': bookmaker_name_list,
      'last_update_time': last_update_time_list,
      'bet_side': bet_side_list,
      'moneyline': money_line_list
   }

   # converting to a a DataFrame
   game_df = pd.DataFrame(game_dict)

   # fixing the times of the games to my timezone
   game_df['game_time'] = pd.to_datetime(game_df.loc[:,'game_time'])
   game_df['game_time'] = game_df.loc[:,'game_time'].dt.tz_convert('US/Central')

   # extracting date
   game_df['date'] = game_df['game_time'].dt.date

   return game_df

# iterates through the different games
def handle_moneylines(lines_json):
   
   game_df_list = []
   for game in lines_json:
      game_df = handle_game(game)
      game_df_list.append(game_df)

   games_df = pd.concat(game_df_list)
   games_df.reset_index(drop=True, inplace=True)

   return games_df

# main scripting function
def get_moneylines():
   
   # sport_keys = ['soccer_epl', 'basketball_nba', 'icehockey_nhl']
   sport_keys = ['basketball_nba']

   sport_df_list = []

   for sport_key in sport_keys:
      moneylines = request_moneylines(sport_key)
      sport_df = handle_moneylines(moneylines)
      sport_df_list.append(sport_df)

   sports_df = pd.concat(sport_df_list)
   sports_df.reset_index(drop=True, inplace=True)

   sports_df['last_update_time'] = pd.to_datetime(sports_df['last_update_time'])
   sports_df['payout'] = sports_df['moneyline'].map(get_payout)
   sports_df['implied_odds'] = sports_df['moneyline'].map(get_impl_prob)

   date = str(datetime.datetime.now().date()) + ' ' + str(datetime.datetime.now().time())

   eligible_bookmakers = ['BetMGM', 'DraftKings', 'FanDuel', 'Bovada']

   sports_df = sports_df[sports_df['bookmaker_name'].isin(eligible_bookmakers)]

   sports_df.to_csv('../bets_today.csv')
   sports_df.to_csv('../logs/bets_' + str(date) + '.csv')

   return sports_df

get_moneylines()