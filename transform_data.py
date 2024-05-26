import os
import getpass
import pandas as pd
import glob
from openai import OpenAI
import copy
import numpy as np
import json
import logging
from utils.openai_utils import set_api_key , get_fielder_locn, get_ball_length, get_ball_line, get_wicket
from utils.helper import get_stats
from utils.constants import IPL_T20_COMM_LOCN, CB_COMM_LOCN, MERGED_COMM_LOCN, MERGED_COMM_CLEAN_LOCN ,BALL_LENGTHS, SCORES_LOCN, SCORES_FILE

logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s - %(levelname)s - %(message)s')


def extract_data_from_commentary():
    """Function to get additional data fields and statistics from the commentary data
    """
    set_api_key()
    cb_files = glob.glob(os.path.join(CB_COMM_LOCN,'*.csv'))
    ipl_files = glob.glob(os.path.join(IPL_T20_COMM_LOCN,'*.csv'))
    for cb in cb_files:
        if not os.path.exists(os.path.join(MERGED_COMM_LOCN,os.path.basename(cb))):
            df_cb = pd.read_csv(cb)
            ipl_fname = [f for f in ipl_files if os.path.basename(cb)[:-4].split('_')[1] in f][0]
            df_ipl = pd.read_csv(ipl_fname)
            df_merged = df_cb.merge(df_ipl, how='inner',left_index=True, right_index=True)
            df_merged['Commentary_y'].type = df_merged['Commentary_y'].astype(str)
            df_merged['Commentary_x'].type = df_merged['Commentary_x'].astype(str)
            df_merged['Commentary_y'] = df_merged['Commentary_y'].apply(lambda x:x.replace('!','')).apply(lambda x:x.strip(' '))
            df_merged['Length'] = df_merged['Commentary_y'].apply(lambda x:x.split('ball')[0] if 'ball' in x else('full toss' if 'full toss' in x else x))
            df_merged['Length'] = df_merged['Length'].apply(lambda x:x if 'Yorker' in x or 'length' in x or 'toss' in x else '')
            df_merged['Length'] = df_merged['Length'].apply(lambda x:x.strip(' ').lower() if type(x)==str else x)
            df_merged['Length'] = df_merged['Length'].apply(lambda x:x.split('length')[0] if (type(x)==str and 'length' in x) else x)
            df_merged['Length'].apply(lambda x:x.strip(' ') if x.strip(' ') in BALL_LENGTHS else (x.strip(' ').split(' ')[-1] if len(x.split(' '))>3 else x.strip(' '))).value_counts()
            df_merged['Line'] = df_merged['Commentary_y'].apply(lambda x:x.split('ball')[1] if len(x.split('ball'))>1 else x)
            df_merged['Line'] = df_merged['Line'].apply(lambda x:x.split('stump')[0])
            df_merged['Line'] = df_merged['Line'].apply(lambda x:x.split('pitching')[1] if 'pitching' in x else x)
            df_merged['Line'] = df_merged['Line'].apply(lambda x:x.strip(',').strip(' '))
            df_merged['Line'] = df_merged['Line'].apply(lambda x:x if ('leg' in x or 'middle' in x or 'off' in x) else '')
            df_merged['Scoring region']=df_merged['Commentary_x'].apply(get_fielder_locn)
            df_merged.to_csv(os.path.join(MERGED_COMM_LOCN,os.path.basename(cb)),index=False)
            del df_cb, df_ipl, df_merged
        else:
            logging.info(f"Merged commentary for {os.path.basename(cb)[:-4]} already exists")

        for cb in cb_files:
            if not os.path.exists(os.path.join(MERGED_COMM_CLEAN_LOCN,os.path.basename(cb))):
                f = os.path.join(MERGED_COMM_LOCN,os.path.basename(cb))
                df_merged = pd.read_csv(f)
                df_inns = get_stats(df_merged)
                df_inns['bowling length'] = df_inns['bowling length'].apply(lambda x:get_ball_length(x) if type(x)==str else x)
                df_inns['bowling line'] = df_inns['bowling line'].apply(lambda x:get_ball_line(x) if type(x)==str else x)
                df['bowling length'].fillna('',inplace=True)
                for i,row in df.iterrows():
                    if df.loc[i,'bowling length']!='nan':
                        if ':' in df.loc[i,'bowling length']:
                            df.loc[i,'bowling length'] = df.loc[i,'bowling length'].split(':')[1].strip(' ')
                df['bowling line'].fillna('',inplace=True)
                for i,row in df.iterrows():
                    if df.loc[i,'bowling line']!='nan':
                        if ':' in df.loc[i,'bowling line']:
                            df.loc[i,'bowling line'] = df.loc[i,'bowling line'].split(':')[1].strip(' ')
                
                df_inns.to_csv(os.path.join(MERGED_COMM_CLEAN_LOCN+os.path.basename(f)),index=False)
            else:
                logging.info(f"Cleaned commentary for {os.path.basename(cb)[:-4]} already exists")
        all_files = glob.glob(os.path.join(MERGED_COMM_CLEAN_LOCN, "*.csv"))
        df=[]
        for f in all_files:
            df_tmp = pd.read_csv(f)
            df_tmp['id'] = os.path.basename(f)[:-4]
            df.append(df_tmp)
    df=pd.concat(df,ignore_index=True)
    df['bowling length'].fillna('',inplace=True)
    for i,row in df.iterrows():
        if df.loc[i,'bowling length']!='nan':
            if ':' in df.loc[i,'bowling length']:
                df.loc[i,'bowling length'] = df.loc[i,'bowling length'].split(':')[1].strip(' ')
    df['Batsman dismissal'] = None
    df['Bowler dismissal'] = None
    df['Fielder dismissal'] = None
    df['Mode of dismissal'] = None
    for i,row in df.iterrows():    
        if not pd.isnull(df.loc[i,'Dismissal']):
            bowler_dismissal = None
            batsman_dismissal = None
            fielder_dismissal = None
            mode = None
            dismissal = df.loc[i,'Dismissal']
            if 'WICKET' in dismissal:
                dismissal = dismissal.split('WICKET')[-1]
            if ' c ' in dismissal and ' b ' in dismissal:
                batsman_dismissal = dismissal.split(' c ')[0].strip(' ' )
                fielder_dismissal = dismissal.split(' c ')[1].split(' b ')[0].strip(' ' )
                bowler_dismissal = dismissal.split(' c ')[1].split(' b ')[1].strip(' ' )
                mode = 'Fielder caught'
            elif ' st ' in dismissal and ' b ' in dismissal:
                batsman_dismissal = dismissal.split(' st ')[0].strip(' ' )
                fielder_dismissal = dismissal.split(' st ')[1].split(' b ')[0].strip(' ' )
                bowler_dismissal = dismissal.split(' st ')[1].split(' b ')[1].strip(' ' )
                mode = 'Stumping'
            elif 'run out' in dismissal:
                batsman_dismissal = dismissal.split(' run out ')[0].strip(' ' )
                fielder_dismissal = dismissal.split(' run out ')[1].strip(' ' )
                bowler_dismissal = None
                mode = 'Run out'
            elif ' lbw ' in dismissal:
                batsman_dismissal = dismissal.split(' lbw ')[0].strip(' ' )
                fielder_dismissal = None
                bowler_dismissal = dismissal.split(' lbw ')[1].strip(' ' )
                mode ='LBW'
            elif ' b ' in dismissal  and ' c ' not in dismissal and ' st ' not in dismissal:
                batsman_dismissal = dismissal.split(' b ')[0].strip(' ' )
                bowler_dismissal = dismissal.split(' b ')[1].strip(' ' )
                fielder_dismissal = None
                mode = 'Bowled'
            elif 'c&amp;b' in dismissal:
                batsman_dismissal = dismissal.split(' c&amp;b ')[0].strip(' ' )
                bowler_dismissal = dismissal.split(' c&amp;b ')[1].strip(' ' )
                fielder_dismissal = bowler_dismissal
                mode = 'Caught and bowled'
            elif 'Obstructing' in dismissal:
                mode = 'Obstructing the field'
                batsman_dismissal = row['Batsman']
                bowler_dismissal = None
                fielder_dismissal = None
            if 'Obstructing' not in dismissal and ' c ' not in dismissal and ' b ' not in dismissal and ' lbw ' not in dismissal and ' run out ' not in dismissal and 'c&amp;b' not in dismissal:
                x=get_wicket(dismissal)
                try:
                    x=json.loads(x.split('```')[1].strip('json').replace('\'','"'))
                    mode = x['mode of dismissal']
                    batsman_dismissal = x['batsman']
                    if mode in ['Fielder caught','Run out','Stumping']:
                        fielder_dismissal = x['fielder involved']
                    elif mode in ['Fielder caught','Stumping','LBW','Bowled']:
                        bowler_dismissal = row['Bowler']
                except Exception as e:
                    logging.error(f"Error {e} encountered")
            df.loc[i,'Batsman dismissal'] = batsman_dismissal
            df.loc[i,'Bowler dismissal'] = bowler_dismissal
            df.loc[i,'Fielder dismissal'] = fielder_dismissal
            df.loc[i,'Mode of dismissal'] = mode
            del batsman_dismissal, bowler_dismissal, fielder_dismissal

    df.to_csv(os.path.join(SCORES_LOCN, SCORES_FILE),index=False)
