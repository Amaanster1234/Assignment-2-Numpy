Assignment 2: NumPy NBA Player Analysis

Purpose
This program uses Python and NumPy to analyze NBA regular season player statistics. It computes performance metrics for each player in each season and produces Top N lists for each metric.

How it works
1) Loads NBA_Player_Stats.tsv using NumPy genfromtxt
2) Extracts needed columns into ndarrays
3) Computes metrics using vectorized NumPy operations
4) Uses argsort to rank player season rows by each metric
5) Saves ranked Top N results to TSV files in the outputs folder

Metrics computed
- Field goal accuracy = FGM / FGA
- Three point accuracy = 3PM / 3PA
- Free throw accuracy = FTM / FTA
- Points per minute = PTS / MIN
- Points per game = PTS / GP
- Overall shooting accuracy = (FGM + 3PM + FTM) / (FGA + 3PA + FTA)
- Blocks per game = BLK / GP
- Steals per game = STL / GP

Division by zero
If a denominator is 0, the result is set to NaN using np.where. NaN values are pushed to the bottom so they do not appear in the Top lists.

How to run
1) Put main.py and NBA_Player_Stats.tsv in the same folder
2) Run:
   python main.py
3) Use the menu to preview metrics or save output files

Outputs
The program creates an outputs folder and writes TSV files like:
top_100_field_goal_accuracy.tsv
Each file contains Rank, Player, Season, Value.