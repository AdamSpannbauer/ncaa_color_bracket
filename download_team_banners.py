import requests
from bs4 import BeautifulSoup
from urllib import urlretrieve
import pandas as pd
import string

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

#function to convert school name to jpg file name
def create_file_name(school):
	clean = str(school).translate(None, string.punctuation + ' ')
	return clean + '.jpg'

#convert school name to jpg file name
school_df['team_jpg'] = school_df['name'].apply(create_file_name)

#iterate over rows to download team logos
for i, row in school_df.iterrows():
	#scrape html
	r = requests.get(row['url_ext'])
	soup = BeautifulSoup(r.text, "html5lib")

	try:
		#extract logo url and save to file
		logo_url = soup.select('.large > img')[0]['src']
		urlretrieve(logo_url, 'team_banners/{}'.format(row['team_jpg']))
	except:
		print('failed to retrieve from {}'.format(row['url_ext']))
