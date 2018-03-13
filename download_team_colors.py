import requests
from bs4 import BeautifulSoup
import pandas as pd
import numpy as np
import re

#set up urls of interest
base_url = 'https://www.ncaa.com'
score_url = '/scoreboard/basketball-men/d1/2018/03/'
day_urls = [str(x) for x in range(13, 17)]

#iterate over days of interest
school_df_list = []
for day in day_urls:
	url = base_url + score_url + day
	
	#scrape html
	r = requests.get(url)
	soup = BeautifulSoup(r.text, "html5lib")
	
	#get team urls and names
	schools = soup.select('.team a')
	school_dict = {x['title']: base_url + x['href'] for x in schools}
	
	#convert data into 2 column df with title and team url
	school_df_i = pd.DataFrame(school_dict.items())
	#add to list
	school_df_list.append(school_df_i)

#combine df list into single df
school_df = pd.concat(school_df_list, ignore_index=True)
#rename
school_df.columns = ['name', 'url_ext']

#function to get teams color from their NCAA page
def get_team_color(url):
	r = requests.get(url)
	soup = BeautifulSoup(r.text, "html5lib")
	
	#try to extract hex color from tile on page
	#na if error
	try:
		color_str = soup.select('.heading .tile-icon')[0]['style']
		color_out = re.findall(r'#.{6}', color_str)[0]
	except:
		color_out = np.nan
	return color_out

#get school colors
school_df['color'] = school_df['url_ext'].apply(get_team_color)

#save to file
school_df.to_csv('data/school_color_df.csv')
