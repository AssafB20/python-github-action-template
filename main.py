import logging
import logging.handlers
import os

import requests

from email.mime.text import MIMEText
from email.mime.application import MIMEApplication
from email.mime.multipart import MIMEMultipart
from smtplib import SMTP
import smtplib
import sys

from bs4 import BeautifulSoup 
    
import pandas as pd  

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
logger_file_handler = logging.handlers.RotatingFileHandler(
    "status.log",
    maxBytes=1024 * 1024,
    backupCount=1,
    encoding="utf8",
)
formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
logger_file_handler.setFormatter(formatter)
logger.addHandler(logger_file_handler)

try:
    SOME_SECRET = os.environ["SOME_SECRET"]
except KeyError:
    SOME_SECRET = "Token not available!"
    #logger.info("Token not available!")
    #raise


if __name__ == "__main__":
    logger.info(f"Token value: {SOME_SECRET}")

    def update_scores():
        global df_scores
        url = 'https://www.basketball-reference.com/leagues/NBA_2023_standings.html#all_confs_standings_E'
        data = requests.get(url)

        with open("stats.html", "w+") as f:
            f.write(data.text)

        with open("stats.html") as f:
            page = f.read()

        soup = BeautifulSoup(page, 'html.parser')

        confs_standings_E = soup.find(id='confs_standings_E')
        confs_standings_W = soup.find(id='confs_standings_W')

        confs_standings = pd.read_html(str(confs_standings_E) + str(confs_standings_W))

        df_E = confs_standings[0]
        df_W = confs_standings[1]
        df_E.rename({'Eastern Conference': 'Team'}, axis=1, inplace=True)
        df_W.rename({'Western Conference': 'Team'}, axis=1, inplace=True)

        df_all = pd.concat([df_E, df_W], axis=0)
        df_all.reset_index(drop=True, inplace=True)

        df_all['Team'] = df_all['Team'].str.split()

        for index, row in df_all.iterrows():
            df_all['Team'][index] = row['Team'][-2]

        df = df_all[['Team','W','L']]

        Assaf = {'W':['Warriors','Lakers','76ers','Hawks'],'L':['Pistons','Hornets'], 'score':'', 'name':'Assaf'}
        Iddo = {'W':['Bucks','Celtics','Suns','Bulls'], 'L':['Jazz','Kings'], 'score':'','name':'Iddo'}
        Liad = {'W': ['Cavaliers','Nets','Rapators','Pelicans'],'L':['Rockets','Thunder'], 'score':'','name':'Liad'}
        Yaniv = {'W':['Nuggets','Maverics','Timberwolves'],'L':['Spurs','Magic','Knicks'], 'score':'','name':'Yaniv'}
        Berger = {'W':['Grizzlies','Clippers','Heat'],'L':['Pacers','Wizards','Blazers'], 'score':'','name':'Berger'}

        names = [Assaf, Iddo, Liad, Yaniv, Berger]

        for name in names:
            name['score'] = df.loc[df['Team'].isin(name['W']),['W']].sum(axis=0)[0] + df.loc[df['Team'].isin(name['L']),['L']].sum(axis=0)[0]

        df_scores = pd.DataFrame(names).set_index('name').sort_values('score',ascending=False)

    def send_email():
    
        recipients = ['assafb20@gmail.com','yanivh42@gmail.com','iddomac@gmail.com','liad.porat@gmail.com','redberger8@gmail.com'] 
        emaillist = [elem.strip().split(',') for elem in recipients]
        msg = MIMEMultipart()
        msg['Subject'] = "Daily scores update"
        msg['From'] = 'assafb20@gmail.com'


        html = """\
        <html>
          <head></head>
          <body>
            {0}
          </body>
        </html>
        """.format(df_scores.to_html())

        part1 = MIMEText(html, 'html')
        msg.attach(part1)

        mail = smtplib.SMTP('smtp.gmail.com', 587)
        mail.ehlo()

        mail.starttls()

        mail.login('assafb20@gmail.com', 'jpytoageodnctktd')
        mail.sendmail(msg['From'], emaillist , msg.as_string())
        mail.quit()
        
    update_scores()
    
    df_scores
    
    send_email()
