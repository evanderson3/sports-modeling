import pandas as pd

import moneylines
import fivethirtyeight

def join():

   moneylines = pd.read_csv("../bets_today.csv", index_col=0)
   forecasts = pd.read_csv("../forecasts_today.csv", index_col=0)

   # print(moneylines[['home_team', 'away_team', 'bet_side']])
   # print(forecasts[['team1', 'team2', 'bet_side']])
   
   # there are some games we are not getting, nba maybe?

   # merging forecast with moneylines
   bets = moneylines.merge(forecasts, left_on = ['date', 'bet_side'], right_on = ['date', 'bet_side'])

   # subsetting some columns
   columns = ['last_update_time', 'league', 'date', 'game_time', 'home_team', 'away_team', 'bet_side', 'bookmaker_name', 'moneyline', 'payout', 'implied_odds', 'win_prob']
   bets = bets[columns]

   # calculating expected value
   bets['exp_val'] = round((bets.loc[:,'win_prob'] * bets.loc[:,'payout']) + (-1*(1-bets.loc[:,'win_prob'])), 3)
   
   # calculating bet size
   roll_size = 25
   bets['kelly_pct'] = round(bets.loc[:,'win_prob'] + ((bets.loc[:,'win_prob']-1)/bets.loc[:,'payout']), 3)
   bets['bet_amnt'] = bets.loc[:,'kelly_pct'].map(lambda x: round(x * roll_size, 0) if x > 0 else 0)

   # writing to csv
   bets.to_csv('../bets.csv')

   return True

def main():
   join()

main()