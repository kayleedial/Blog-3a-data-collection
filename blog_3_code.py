import pandas as pd 
import numpy as np 
import requests
from bs4 import BeautifulSoup

# read in first dataset (oscars list)
oscars = pd.read_csv("blog3/the_oscar_award.csv")
oscars['category'].value_counts().shape
oscars = oscars.drop(['year_film','year_ceremony'], axis=1)
oscars.head(15)

# filter out all data that isn't best picture / best motion picture
oscars['category'] = oscars['category'].str.lower()
bp = oscars[(oscars['category'] == 'best picture') | (oscars['category'] == 'best motion picture')]
bp


# web scrape rotten tomatoes data
url_list = ['https://editorial.rottentomatoes.com/guide/oscars-2023-best-picture-nominees/',
            'https://editorial.rottentomatoes.com/guide/2022-best-picture-nominees/', 
            'https://editorial.rottentomatoes.com/guide/2021-best-picture-nominees-ranked-by-tomatometer/',
            'https://editorial.rottentomatoes.com/guide/oscars-2020-best-picture-nominees-ranked-by-tomatometer/',
            'https://editorial.rottentomatoes.com/article/oscars-2019-best-picture-nominees/',
            'https://editorial.rottentomatoes.com/article/all-2018-oscar-best-picture-nominees-by-tomatometer/',
            'https://editorial.rottentomatoes.com/guide/oscars-2017-best-picture-nominees-tomatometer-scores/',
            'https://editorial.rottentomatoes.com/guide/oscars-best-picture-nominees-ranked-by-tomatometer/',
            'https://editorial.rottentomatoes.com/article/2015-oscar-nominations/',
            'https://editorial.rottentomatoes.com/article/total-recall-the-2014-best-picture-nominees/',
            'https://editorial.rottentomatoes.com/article/2013-academy-awards-nominations/',
            'https://editorial.rottentomatoes.com/guide/lowest-rated-best-picture-nominees-of-all-time/',
            "https://editorial.rottentomatoes.com/guide/movies-100-percent-score-rotten-tomatoes/", 
            "https://editorial.rottentomatoes.com/guide/oscars-best-and-worst-best-pictures/",
            "https://editorial.rottentomatoes.com/guide/best-cinematography-winners-ranked/",
            "https://editorial.rottentomatoes.com/guide/golden-globes-best-film-winners-by-tomatometer/"
            ]


toms = pd.DataFrame(columns=['Title', 'Tomato Score', 'Year', 'Critic Review'])

for url in url_list:
    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'html.parser')
    movies = soup.find_all('div', {'class': 'countdown-item-content'})
    for movie in movies:
        title = movie.find('a').text
        tomato_score = movie.find('span', {'class': 'tMeterScore'}).text
        year = movie.find('span', {'class': 'subtle start-year'}).text
        critic_review = movie.find('div', {'class': 'info critics-consensus'}).text.strip()
        toms = toms.append({'Title': title, 'Tomato Score': tomato_score, 'Year': year, 'Critic Review': critic_review}, ignore_index=True)

print(toms)
toms.shape
toms.head(50)

# remove duplicate values
tomats = toms.drop_duplicates()
tomats.shape

# take parentheses off of the year and remove 'Critics Consensus: '
tomats['Year'] = tomats['Year'].str.replace('(', '').str.replace(')', '')
tomats['Critic Review'] = tomats['Critic Review'].str.replace('Critics Consensus: ', '')

# check to see if we have movies with the same titles
tomats['Title'].value_counts()

# 1st - Mutiny on the Bounty
tomats[tomats['Title'] == 'Mutiny on the Bounty']
bp[bp['film'] == 'Mutiny on the Bounty'] # it's only been a nominee once (1962/70% version)
# remove the other version:
tomats = tomats[~((tomats['Title'] == 'Mutiny on the Bounty') & (tomats['Tomato Score'] == '96%'))]

# 2nd - All Quiet
tomats[tomats['Title'] == 'All Quiet on the Western Front']
bp[bp['film'] == 'All Quiet on the Western Front'] # it's only been a nominee once (2022/90% version)
# remove the other version:
tomats = tomats[~((tomats['Title'] == 'All Quiet on the Western Front') & (tomats['Tomato Score'] == '98%'))]

# 3rd - Cleopatra
tomats[tomats['Title'] == 'Cleopatra']
bp[bp['film'] == 'Cleopatra'] # it's only been a nominee once (1963/56% version)
# remove the other version:
tomats = tomats[~((tomats['Title'] == 'Cleopatra') & (tomats['Tomato Score'] == '82%'))]

# 4th - A Star Is Born
tomats[tomats['Title'] == 'A Star Is Born']
bp[bp['film'] == 'A Star Is Born'] # the wrong one is in the tomats
# remove one of them:
tomats = tomats[~((tomats['Title'] == 'A Star Is Born') & (tomats['Tomato Score'] == '35%'))]
# change the 100% version to 90%
tomats.loc[tomats['Title'] == 'A Star Is Born', 'Tomato Score'] = '90%'

# 5th - West Side Story
tomats[tomats['Title'] == 'West Side Story']
bp[bp['film'] == 'West Side Story'] 
# remove one of them:
tomats = tomats[~((tomats['Title'] == 'West Side Story') & (tomats['Tomato Score'] == '92%'))]

##### no more duplicate titles
tomats['Title'].value_counts()

# change 'Title' to 'film'
tomats['film'] = tomats['Title']
tomats = tomats.drop('Title', axis=1)

# merge oscars with the tomatoes scores
df_m = pd.merge(bp, tomats, how='inner', on=['film'])

# 2023 oscars winner column has not been populated
# fill all NAs with False
df_m['winner'] = df_m['winner'].fillna(False)

# set Everything Everywhere to True
df_m.loc[df_m['film'] == 'Everything Everywhere All at Once', 'winner'] = True

# 237 rows & 8 columns
df_m.shape
df_m = df_m.drop('category', axis=1)
df_m.to_csv('movies.csv')





