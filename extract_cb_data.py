import re
import pandas as pd
import glob
import os
from utils.constants import SCHEDULE_URL, CB_URL, CB_DF_COLS, CB_SCHEDULE_LOCN, CB_COMM_LOCN, IPL_T20_SCHEDULE_LOCN, SCHEDULE_FILE, \
    COLS_STR, COLS_TO_KEEP
from utils.driver_utils import get_driver, get_data_driver, get_score_driver
from utils.helper import get_inv_home_city_dict
import logging
from datetime import datetime

logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s - %(levelname)s - %(message)s')

def get_schedule_cb():
    """Function to get the schedule data from cricbuzz.com

    Returns:
        pd.DataFrame: Dataframe containing the schedule data
    """
    driver=get_driver()
    schedule_url = SCHEDULE_URL['cb']
    tags_schedule = get_data_driver(schedule_url, driver, 'cb')
    schedule_lst=[]
    inv_home_city_dict = get_inv_home_city_dict()
    for _,tag in enumerate(tags_schedule):
        try:
            location = re.findall(r'\>.*?\<',str(tag.find('div',class_="text-gray")))[0][1:-1].split(',')[1].strip()
            match = re.findall(r'\>.*?\<',str(tag.find('a',class_="text-hvr-underline")))[1][1:-1].split(',')[0]
            if 'cb-text-complete' in str(tag):
                url = tag.find('a',class_="cb-text-complete")['href']
                url = url.replace('scores','full-commentary')
                dt = '2024 '+re.findall(r'\>.*?\<',str(tag.find('span',class_="ng-binding")))[0][1:-1]
                tm = re.findall(r'\>.*?\<',str(tag.find('div',class_="cb-col-40 cb-col cb-srs-mtchs-tm")))
                dt_tm = dt + ' ' + tm[tm.index('> LOCAL<')-1][1:-1].strip(' ')
                date = datetime.strptime(dt_tm,'%Y %b %d, %a %I:%M %p').strftime('%Y-%m-%d %H:%M')
                if 'qualifier' not in url and 'final' not in url and 'eliminator' not in url:
                    home_team = inv_home_city_dict[location.strip(' ')]
                    away_team = [t.strip() for t in match.split('vs')if t.strip(' ')!=home_team][0]
                else:
                    team1 = [t.strip() for t in match.split('vs')if t.strip(' ')][0]
                    team2 = [t.strip() for t in match.split('vs')if t.strip(' ')][1]
                    teams =[team1, team2]
                    teams.sort()
                    home_team = teams[0]
                    away_team = teams[1]
                match_id = url.split('/')[2]
                url = CB_URL + url
                logging.info('Extracted information for {}'.format(match))
                schedule_lst.append([match_id,date,location,home_team, away_team,url]) 
        except Exception as e:
            logging.exception(f"Exception {e} encountered")
    df_schedule=pd.DataFrame(schedule_lst,columns=CB_DF_COLS)
    if not os.path.exists(os.path.join(IPL_T20_SCHEDULE_LOCN,SCHEDULE_FILE)):
        logging.error('Schedule file from iplt20.com not present.')
    else:
        df_schedule_iplt20 = pd.read_csv(os.path.join(IPL_T20_SCHEDULE_LOCN,SCHEDULE_FILE))
        cols = COLS_STR
        for c in cols:
            df_schedule[c].type = df_schedule[c].astype(str)
            df_schedule_iplt20[c].type = df_schedule_iplt20[c].astype(str)
        df_schedule_merge = df_schedule.merge(df_schedule_iplt20,how='inner',on=cols)
        cols_to_keep = COLS_TO_KEEP
        df_schedule_merge = df_schedule_merge[cols_to_keep]
        for c in cols_to_keep:
            if '_x' in c:
                df_schedule_merge.rename(columns={c:c[:-2]},inplace=True)
        df_schedule_merge.rename(columns={'Match id_y':'Match id_iplt20'},inplace=True)
        if len(df_schedule_merge)>0:
            logging.info(f"Saving the schedule from cricbuzz.com to {CB_SCHEDULE_LOCN}")
            df_schedule_merge.to_csv(os.path.join(CB_SCHEDULE_LOCN,SCHEDULE_FILE),index=False)
            return df_schedule_merge
        else:
            logging.error(f"Error encountered with the schedule file from cricbuzz.com")


def get_commentary_cb(df_schedule):
    """Function to get commentary data from cricbuzz.com

    Args:
        df_schedule (pd.DataFrame): Dataframe containing the schedule from crizbuzz.com
    """
    match_completed = glob.glob(os.path.join(CB_COMM_LOCN,'*.csv'))
    match_completed_id = [os.path.basename(f)[:-4].split('_')[0] for f in match_completed]
    match_ids = df_schedule['Match id'].values.tolist()
    match_id_not_present = [m for m in match_ids if m not in match_completed_id]
    for match_id in match_id_not_present[:5]:
        try:
            results_lst = []
            df_match=df_schedule[(df_schedule['Match id']==match_id)]
            url = df_match['URL'].values.tolist()[0]
            ipl_match_id = df_match['Match id_iplt20'].values.tolist()[0]
            first_batting = df_match['First batting'].values.tolist()[0]
            second_batting = df_match['Second batting'].values.tolist()[0]
            innings=1
            for team in [first_batting, second_batting]:
                driver = get_driver()
                tags = get_score_driver(driver,url,team,source='cb')
                for t in tags:
                    ball = re.findall(r'\>.*?\<',str(t.find('div',class_="cb-col cb-col-8 text-bold ng-scope")))
                    if len(ball)>0:
                        ball_over = ball[1][1:-1]
                        cmtry = re.findall(r'\>.*?\<',str(t.find('p',class_="cb-com-ln ng-binding ng-scope cb-col cb-col-90")))
                        cmtry=[c_elem.strip('>').strip('<') for c_elem in cmtry]
                        cmtry_str=''.join(cmtry)
                        results_lst.append([match_id,ipl_match_id,team,innings,ball_over,cmtry_str])
                logging.info(f"Extracted data for {team} for inning {innings} for match id {match_id}")
                innings+=1
            df_commentary=pd.DataFrame(results_lst,columns=['Match ID','Match ID IPLT20','Team','Innings','Ball','Commentary'])
            if len(df_commentary)>0:
                logging.info(f"Saving the commentary for match {match_id} from cricbuzz.com to {CB_COMM_LOCN}")
                df_commentary.to_csv(os.path.join(CB_COMM_LOCN,str(match_id)+'_'+str(ipl_match_id)+'.csv'),index=False)
            else:
                logging.error(f"Error encountered with the commentary for match {match_id} from cricbuzz.com")
        except Exception as e:
            logging.exception(f"Exception {e} encountered")
