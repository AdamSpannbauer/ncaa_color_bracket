import pandas as pd
import json
import colorsys
import matplotlib.pyplot as plt
import numpy as np

#read in data
color_data = pd.read_csv('data/school_color_df.csv', index_col=0)
with open("data/bracket.json") as f:
	bracket = json.loads(f.read())

def gen_matchups(n):
	"""
	generate seed pairs for a round

	>>> gen_matchups(4)
	[(1, 4), (2, 3)]
	"""
	seeds = range(1, n+1)
	games = []
	for i in range(n/2):
		low = seeds[i]
		hi  = seeds[-(i+1)]
		games.append((low, hi))
	return games

def hex_2_hsv(hex_col):
	"""
	convert hex code to colorsys style hsv

	>>> hex_2_hsv('#f77f00')
	(0.08569500674763834, 1.0, 0.9686274509803922)
	"""
	hex_col = hex_col.lstrip('#')
	r, g, b = tuple(int(hex_col[i:i+2], 16) for i in (0, 2 ,4))
	return colorsys.rgb_to_hsv(r/255.0, g/255.0, b/255.0)

def play_game(a, b):
	"""
	look up each team's color and compare hsv
	return true if team a hsv > team b hsv

	>>> play_game("N.C. Central", "Texas Southern")
	True
	"""
	a_hex = list(color_data.loc[color_data['name'] == a, 'color'])[0]
	b_hex = list(color_data.loc[color_data['name'] == b, 'color'])[0]
	
	a_wins = hex_2_hsv(a_hex) > hex_2_hsv(b_hex)
	
	return a_wins

######################
# PLAY-IN GAMES
######################
#west 16 "NCC/TSU"
a = "N.C. Central"
b = "Texas Southern"
a_wins = play_game(a, b)
bracket['west']['16'] = [b,a][a_wins]

#east 11 "SBU/UCLA"
a = "St. Bonaventure"
b = "UCLA"
a_wins = play_game(a, b)
bracket['east']['11'] = [b,a][a_wins]

#east 16 "LIUB/RAD"
a = "LIU Brooklyn"
b = "Radford"
a_wins = play_game(a, b)
bracket['east']['16'] = [b,a][a_wins]

#midwest 11 "ASU/SYR"
a = "Arizona St."
b = "Syracuse"
a_wins = play_game(a, b)
bracket['midwest']['11'] = [b,a][a_wins]

######################
# BRACKET
######################
rounds = [gen_matchups(x) for x in [16, 8, 4, 2]]
for region, teams in bracket.items():
	for i, r in enumerate(rounds):
		for game in r:
			a = teams[str(game[0])]
			b = teams[str(game[1])]

			a_wins = play_game(a, b)

			teams[str(game[0])] = [b,a][a_wins]

			del teams[str(game[1])]
		
		file_out = 'data/{}_round_{}.json'.format(region, str(i+2))
		with open(file_out, 'w') as f:
			json.dump(teams, f, indent=2)

######################
# FINAL FOUR
######################
#west v midwest
with open('data/west_round_5.json') as f:
	ta = json.loads(f.read())['1']
with open('data/midwest_round_5.json') as f:
	tb = json.loads(f.read())['1']

print('{} WINS THE WEST!!'.format(ta))
print('{} WINS THE MIDWEST!!'.format(tb))

a_wins = play_game(ta, tb)
top_winner = [tb,ta][a_wins]
top_loser  = [ta,tb][a_wins]

#south v east
with open('data/south_round_5.json') as f:
	ba = json.loads(f.read())['1']
with open('data/east_round_5.json') as f:
	bb = json.loads(f.read())['1']

print('{} WINS THE SOUTH!!'.format(ba))
print('{} WINS THE EAST!!'.format(bb))

a_wins = play_game(ba, bb)
bottom_winner = [bb,ba][a_wins]
bottom_loser  = [ba,bb][a_wins]

######################
# CHAMPIONSHIP
######################
top_wins = play_game(top_winner, bottom_winner)

big_winner = [bottom_winner, top_winner][top_wins]
second = [top_winner, bottom_winner][top_wins]

print('\n\n{} WINS IT ALL!!!!!!!'.format(big_winner))

######################
# PLOT FINAL FOUR PODIUM
######################
vals = [4,2,1,1]
labs = [big_winner, second, bottom_loser, top_loser]
cols = [list(color_data.loc[color_data['name'] == x, 'color'])[0] for x in labs]

y_pos = np.arange(len(labs))

plt.bar(y_pos, vals, color = cols)
plt.xticks(y_pos, labs)
plt.yticks([])
plt.title('HSV Final Four Podium')

plt.savefig('readme/hsv_podium.png')

plt.show()


