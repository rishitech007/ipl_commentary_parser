# import libraries
import re
import pandas as pd
import os
from datetime import datetime
from utils.driver_utils import get_driver, get_results_driver
from utils.constants import RESULTS_URL, RESULTS_COLS, CB_SCHEDULE_LOCN, SCHEDULE_FILE, RESULTS_FILE, RESULTS_LOCN
import logging


logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s - %(levelname)s - %(message)s')

def get_results_info():
    """Function to extract results data from iplt20.com and merge it with the schedule file of cricbuzz.com to maintain consistency of keys
    """
    driver = get_driver()
    # Read the IPL schedule
    schedule_url = RESULTS_URL
    tags_schedule = get_results_driver(driver, schedule_url)
    results_lst=[]
    for i in range(len(tags_schedule)):
        try:
            
            location = re.findall(r'\>.*?\<',str(tags_schedule[i].find('div',class_="w50 fl").find('p',class_="ng-binding")))[-1][1:-1].strip()
            home_team = re.findall(r'\>.*?\<',str(tags_schedule[i].find_all('h3',class_="ng-binding ng-scope")[0]))[0][1:-1]
            away_team = re.findall(r'\>.*?\<',str(tags_schedule[i].find_all('h3',class_="ng-binding ng-scope")[2]))[0][1:-1]
            date = re.findall(r'\>.*?\<',str(tags_schedule[i].find('div',class_="w50 fl").find('div',class_="vn-matchDateTime ng-binding")))[0].strip('>').strip('<').strip(' ')
            date = date.split('IST')[0].strip(' ')
            date = date.replace('pm','PM')
            date = '2024 ' + date
            date = datetime.strptime(date,'%Y %b, %a %d , %I:%M %p').strftime('%Y-%m-%d %H:%M')
            result = re.findall(r'\>.*?\<',str(tags_schedule[i].find('div',class_="w20 tl pr50").find('div',class_="vn-ticketTitle ng-binding ng-scope")))[0].strip('>').strip('<').strip(' ')
            url = tags_schedule[i].find('a',class_="vn-matchBtn ng-scope")['ng-href']
            match_id = url.split('/')[-1]
            results_lst.append([match_id,date,location,home_team, away_team,result])
        except Exception as e:
            logging.exception(f"Exception {e} encountered")
    df_results=pd.DataFrame(results_lst,columns=RESULTS_COLS)
    df_results['Match id'] = df_results['Match id'].astype(int)
    df_cb = pd.read_csv(os.path.join(CB_SCHEDULE_LOCN, SCHEDULE_FILE))
    df_results_new = df_cb[['Match id','Match id_iplt20']].merge(df_results,left_on='Match id_iplt20',right_on='Match id',how='inner')
    df_results_new['Match id'] = df_results_new['Match id_x'].astype(str) + '_' + df_results_new['Match id_y'].astype(str)
    df_results_new['Match number'] = df_results_new.index + 1
    df_results_new.drop(columns=['Match id_x','Match id_iplt20','Match id_y'],inplace=True)
    logging.info('Saving results file to {}'.format(os.path.join(RESULTS_LOCN, RESULTS_FILE)))
    df_results_new.to_csv(os.path.join(RESULTS_LOCN, RESULTS_FILE))