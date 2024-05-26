import glob
import os
import logging
import re
import pandas as pd
from utils.constants import SCHEDULE_URL, IPL_T20_DF_COLS, FIRST_INNINGS, IPL_T20, IPL_T20_COMM_DF_COLS, IPL_T20_SCHEDULE_LOCN, SCHEDULE_FILE, \
IPL_T20_COMM_LOCN
from utils.driver_utils import get_driver, get_data_driver, get_score_driver
import logging
from datetime import datetime

logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s - %(levelname)s - %(message)s')

def get_schedule_iplt20():
    """Function to get schedule data from iplt20.com along with any abandoned matches

    Returns:
        (pd.DataFrame, List)): Dataframe containing the schedule of the matches from iplt20.com and the list of abandoned matches
    """
    driver=get_driver()
    schedule_url = SCHEDULE_URL[IPL_T20]
    tags_schedule = get_data_driver(schedule_url, driver, IPL_T20)
    schedule_lst=[]
    abandoned_matches=[]
    for _,tag in enumerate(tags_schedule):
        try:
            location = re.findall(r'\>.*?\<',str(tag.find('div',class_="w50 fl").find('p',class_="ng-binding")))[-1][1:-1].strip()
            home_team = re.findall(r'\>.*?\<',str(tag.find_all('h3',class_="ng-binding ng-scope")[0]))[0][1:-1]
            away_team = re.findall(r'\>.*?\<',str(tag.find_all('h3',class_="ng-binding ng-scope")[2]))[0][1:-1]
            result = re.findall(r'\>.*?\<',str(tag.find('div',class_="w20 tl pr50").find('div',class_="vn-ticketTitle ng-binding ng-scope")))[0].strip('>').strip('<').strip(' ')
            date = re.findall(r'\>.*?\<',str(tag.find('div',class_="w50 fl").find('div',class_="vn-matchDateTime ng-binding")))[0].strip('>').strip('<').strip(' ')
            date = date.split('IST')[0].strip(' ')
            date = date.replace('pm','PM')
            date = '2024 ' + date
            date = datetime.strptime(date,'%Y %b, %a %d , %I:%M %p').strftime('%Y-%m-%d %H:%M')
            if 'First' in str(tag.find_all('h3',class_="ng-binding ng-scope")[1]):
                first_batting = re.findall(r'\>.*?\<',str(tag.find_all('h3',class_="ng-binding ng-scope")[1]))[0][1:-1]
                second_batting = re.findall(r'\>.*?\<',str(tag.find_all('h3',class_="ng-binding ng-scope")[3]))[0][1:-1]
            elif 'Second' in str(tag.find_all('h3',class_="ng-binding ng-scope")[1]):
                first_batting = re.findall(r'\>.*?\<',str(tag.find_all('h3',class_="ng-binding ng-scope")[3]))[0][1:-1]
                second_batting = re.findall(r'\>.*?\<',str(tag.find_all('h3',class_="ng-binding ng-scope")[1]))[0][1:-1]
            url = tag.find('a',class_="vn-matchBtn ng-scope")['ng-href']
            match_id = url.split('/')[-1]
            if result=='Match Abandoned':
                abandoned_matches.append(match_id)
            schedule_lst.append([match_id,date,location,home_team, away_team, first_batting, second_batting, url])
        except Exception as e:
            logging.exception(f"Exception {e} encountered")
    df_schedule=pd.DataFrame(schedule_lst,columns=IPL_T20_DF_COLS)
    if len(df_schedule)>0:
        logging.info(f"Saving the schedule from iplt20.com to {IPL_T20_SCHEDULE_LOCN}")
        df_schedule.to_csv(os.path.join(IPL_T20_SCHEDULE_LOCN,SCHEDULE_FILE),index=False)
        return df_schedule, abandoned_matches
    else:
        logging.error(f"Error encountered with the schedule file from iplt20.com")

def get_commentary_iplt20(df_schedule, abandoned_matches=None):
    """Function to get commentary data from iplt20.com

    Args:
        df_schedule (pd.DataFrame): Dataframe containing the schedule
        abandoned_matches (List, optional): List containing abandoned matches. Defaults to None.
    """
    match_completed = glob.glob(os.path.join(IPL_T20_COMM_LOCN,'/*.csv'))
    match_completed_id = [os.path.basename(f)[:-4] for f in match_completed]
    if abandoned_matches:
        for am in abandoned_matches:
            match_completed_id.append(str(am))
    match_ids = df_schedule['Match id'].values.tolist()
    match_id_not_present = [m for m in match_ids if m not in match_completed_id]
    for match_id in match_id_not_present:
        results_lst = []
        df_match=df_schedule[(df_schedule['Match id']==match_id)]
        url = df_match['URL'].values.tolist()[0]
        first_batting = df_match['First batting'].values.tolist()[0]
        second_batting = df_match['Second batting'].values.tolist()[0]
        innings=FIRST_INNINGS
        for team in [first_batting,second_batting]:
            driver = get_driver()
            tags = get_score_driver(driver, url, team,source='iplt20')
            regex = re.compile('.*cmdOver mcBall.*')
            for t in tags:
                ball_data=str(t.find('p',class_=regex))
                if ball_data:
                    boundary=''
                    wicket = ''
                    if 'bgFour' in ball_data:
                        boundary='four'
                    elif 'bgSix' in ball_data:
                        boundary='six'
                    if 'bgWicket' in ball_data:
                        wicket='W'
                    ball_str = re.findall(r'\>.*?\<',ball_data)
                    if len(ball_str)>0:
                        ball = ball_str[0][1:-1].strip()
                        runs_scored = ball_str[2][1:-1].strip()
                        
                        if runs_scored:
                            if runs_scored!='W':
                                batsman_runs_scored = int(runs_scored)
                            elif runs_scored=='W':
                                batsman_runs_scored = 0
                                runs_scored = 0
                        else:
                            batsman_runs_scored = 0
                        wide = ball_str[3][1:-1].strip()
                        noball = ball_str[4][1:-1].strip()
                        bye = ball_str[5][1:-1].strip()
                        lbye = ball_str[6][1:-1].strip()

                        players = re.findall(r'\>.*?\<',str(t.find('div',class_="commentaryStartText ng-binding ng-scope")))
                        for p in players:
                            p = p.replace('\xa0',' ')
                            if 'bowling to' in p:
                                bowler = p[1:-1].split(' bowling to ')[0]
                                batsman = p[1:-1].split(' bowling to ')[1]
                        comment = re.findall(r'\>.*?\<',str(t.find('div', class_="commentaryText ng-binding")))
                        dismissal=''
                        try:
                            if wicket=='W':
                                dismissal = re.search('(?<=WICKET)(.*)', str(t.find('div', class_="commentaryText ng-binding")))[0].split('(')[0].strip(' ')
                        except Exception as e:
                            logging.exception(f"Exception {e} encountered")
                        
                        cmtry = ''.join([t.strip('>').strip('<').strip(' ').replace(u'\xa0', u' ').replace('&amp','&') 
                                        for t in comment if len(t)>2 and 
                                        not t.strip('>').strip('<').strip(' ').replace(u'\xa0', u'').isupper()])
                        if wide:
                            runs_scored = int(re.search(r'\d+', wide).group())
                        elif bye:
                            runs_scored = int(re.search(r'\d+', bye).group())
                        elif lbye:
                            runs_scored = int(re.search(r'\d+', lbye).group())
                        elif noball:
                            runs_scored = int(re.search(r'\d+', noball).group())
                            if 'bye' in cmtry:
                                batsman_runs_scored = 0
                                if 'leg bye' in cmtry:
                                    lbye = str(runs_scored - 1)+' LB'
                                else:
                                    bye = str(runs_scored - 1)+' B'

                            else:
                                batsman_runs_scored = runs_scored - 1
                        results_lst.append([match_id,team,innings,ball,batsman, bowler, runs_scored, batsman_runs_scored,boundary,wicket, dismissal, wide, noball, bye, lbye,cmtry])
            logging.info(f"Extracted data for {team} for inning {innings} for match id {match_id}")
            innings+=1
        df_commentary=pd.DataFrame(results_lst,columns=IPL_T20_COMM_DF_COLS)
        if len(df_commentary)>0:
            logging.info(f"Saving the commentary for match {match_id} from iplt20.com to {IPL_T20_COMM_LOCN}")
            df_commentary.to_csv(os.path.join(IPL_T20_COMM_LOCN,str(match_id)+'.csv'),index=False)
        else:
            logging.error(f"Error encountered with the commentary for match {match_id} from iplt20.com")