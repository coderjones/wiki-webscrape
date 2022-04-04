import requests 
from bs4 import BeautifulSoup
import pandas as pd
import regex as re

#Used headers/agent because the request was timed out and asking for an agent. 
#Using following code we can fake the agent.
headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:88.0) Gecko/20100101 Firefox/88.0'}

# Get list of USA cities by population via wikipedia
response = requests.get("https://en.wikipedia.org/wiki/List_of_United_States_cities_by_population",headers=headers)

content = response.content

soup = BeautifulSoup(content,"html.parser")
#soup = BeautifulSoup(content,"lxml")

# get the right table
table = soup.find("table",attrs={"class": "wikitable sortable"})

table_body = table.find('tbody')

data = []
rows = table_body.find_all('tr')

# for the rows in the table
for row in rows:
    rank_th = row.find_all('th')
    
    # City rank
    rank = rank_th[0].text.strip()

    cols = row.find_all('td')

    # Get rid of special characters
    cols = [ele.text.strip().replace(r'[^.a-zA-Z0-9]',"") for ele in cols]

    new_cols = []

    new_cols.append(rank)

    # String cleanup
    for i in cols:
        i = re.sub(r'\[.\]',"",i)
        i = re.sub(r'[^.a-zA-Z0-9\s]',"", i)
        i = i.replace('\xa0'," ")
        new_cols.append(i)

    if len(new_cols) == 11:

        #print(new_cols)
        # strip sq mi/km2
        new_cols[6] = new_cols[6].replace("sq mi", "").strip()
        new_cols[8] = new_cols[8].replace("sq mi", "").strip()
        new_cols[7] = new_cols[7].replace("km2","").strip()
        new_cols[9] = new_cols[9].replace("km2","").strip()

        # Split long/lat into separate cols
        s = new_cols[10].split(' ')
        long_lat = s[3] + " " + s[4]
        new_cols[10] = s[3]
        new_cols.append(s[4])

    data.append([ele for ele in new_cols if ele]) # Get rid of empty values

df = pd.DataFrame(data)
df.columns = ['City Rank','City','State','2020 census','2010 census','Change','2020 land area sq mi','2016 land area km2','2020 pop density sq mi','2016 pop desity km2','longitude','latitude']

del df['Change'] # we don't need this

# plot the data
import matplotlib.pyplot as plt

plt.style.use('ggplot')
plt.style.use('seaborn-darkgrid')

df.to_csv("us_populations.csv",index=False)
print("done")

# read us_populations.csv into df1
df1 = pd.read_csv("us_populations.csv")

# plot the data by top 10 cities by population
df1.sort_values(by=['2020 census'],ascending=False,inplace=True)
df1.head(10).plot(kind='bar',x='City',y='2020 census')
plt.title("Top 10 cities by population")
plt.xlabel("City")
plt.ylabel("Population")
plt.show()
