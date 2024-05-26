from .constants import HOME_CITY_DICT
import numpy as np
import pandas as pd


def get_inv_home_city_dict():
    """Helper function to get the inverse of the team and their home ground(s). A team can have more than 1 home ground.

    Returns:
        (dict): INverted dictionary containing the ground as the key and the team as the value
    """
    inv_home_city_dict={}
    for k,v in HOME_CITY_DICT.items():
        for v_elem in v:
            if v_elem not in inv_home_city_dict:
                inv_home_city_dict[v_elem]=k
    return inv_home_city_dict


def total_balls(over):
    """Helper function to compute total number of balls in an over

    Args:
        over (float): Over containing ball information

    Returns:
        (int): The ball number being bowled
    """
    if over%1 == 0: 
        return over*6
    return int(6*(over//1)) + int(np.round(10*(over%1)))


def get_stats(df_merged):
    """Function to get additional statistics from the dataframe

    Args:
        df_merged (pd.DataFrame): Dataframe containing the data of the players

    Returns:
        pd.DataFrame: Transformed dataframe containing the additional statistics
    """
    cols_to_use=['Match ID_x','Match ID_y','Team_x','Innings_x','Ball_x','Batsman','Bowler','Runs','Batsman runs','Boundary',
             'Wicket','Dismissal','Wide','No ball','Bye','Leg bye','Length','Line','Scoring region']
    df_inns=df_merged[cols_to_use].rename(columns={'Team_x':'Team','Innings_x':'Innings','Ball_x':'Ball'})
    df_inns['id'] = df_merged['Match ID_x'].astype(str)+'_'+df_merged['Match ID_y'].astype(str)
    del df_merged['Match ID_x']
    del df_merged['Match ID_y']
    # Logic for how many balls a batsman has faced. This includes no balls, byes, and leg byes. Wides are excluded.
    df_inns['Balls faced'] = df_inns['Wide']
    df_inns.loc[~df_inns['Balls faced'].isna(),'Balls faced']=0
    df_inns.loc[df_inns['Balls faced'].isna(),'Balls faced']=1
    # Sort data by innings
    df_inns.index.name = 'MyIdx'
    df_inns.sort_values(by = ['Innings', 'MyIdx'], ascending = [True, False], inplace=True)
    # Calculate per batsman runs for each ball faced
    df_inns['Per batsman runs']=df_inns.groupby(['Innings','Batsman'])['Batsman runs'].cumsum()
    df_inns['Balls faced'] = df_inns['Balls faced'].astype(int)
    df_inns['Per batsman ball faced']=df_inns.groupby(['Innings','Batsman'])['Balls faced'].cumsum()
    # Calculate batsman strike rate
    df_inns['Batsman strike rate'] = 100*df_inns['Per batsman runs']/(df_inns['Per batsman ball faced']+0.00000000001)
    # Calculate team score
    df_inns['Team score'] = df_inns.groupby(['Innings'])['Runs'].cumsum()
    # Calculate batsman order
    df_inns['Batsman order']=df_inns.groupby(['Innings'])['Batsman'].transform(lambda x: pd.factorize(x)[0]+1)
    # Calculate legitimiate ball faced 
    df_inns['Legit ball'] = df_inns['Ball'].apply(total_balls)
    # Calculate run rate
    df_inns['Run rate'] = 6.0*df_inns['Team score']/df_inns['Legit ball']
    # Calculate target and estimate required run rate for team batting second
    target = df_inns[df_inns['Innings']==1]['Team score'].max()
    df_inns['RRR'] = 'NULL'
    df_inns.loc[df_inns['Innings']==2,'RRR']= 6*(target - df_inns['Team score'])/(120 - df_inns['Legit ball'])
    df_inns['RRR']=df_inns['RRR'].replace(np.inf,'NULL')
    df_inns['RRR'].apply(lambda x: x if type(x)==float else x)
    # Calculate the over number
    df_inns['Over'] = df_inns['Ball'].apply(lambda x:int(x)+1)
    # Calculcate how many runs conceded by the bowler. Excludes byes and leg-byes
    df_inns['Bowler runs'] = 0
    df_inns.loc[(df_inns['Leg bye'].isna())&(df_inns['Bye'].isna()),'Bowler runs'] = df_inns.loc[(df_inns['Leg bye'].isna())&(df_inns['Bye'].isna()),'Runs']
    # Calculate the over and ball number bowled by the bowler
    df_inns['Bowler over']=df_inns.groupby(['Innings','Bowler'])['Over'].transform(lambda x: pd.factorize(x)[0])
    df_inns['Bowler over ball'] = df_inns['Ball']%1
    # Calculate runs per over conceded by the bowler
    df_inns['RPO']=df_inns.groupby(['Innings','Bowler'])['Bowler runs'].cumsum()/(df_inns['Bowler over']+df_inns['Bowler over ball']*10/6)
    df_inns.rename(columns={'Batsman runs':'runs scored','Runs':'runs plus extras','Line':'bowling line','Length':'bowling length','Batsman strike rate':'Cumulative batsman strike rate'},
              inplace=True)
    cols_extras=['Wide','No ball','Leg bye','Bye']
    for c in cols_extras:
        df_inns[c].fillna(0,inplace=True)
        df_inns[c] = df_inns[c].apply(lambda x: int(x.split(' ')[0]) if type(x)==str else x)
        df_inns[c] =df_inns[c].astype(int)
    return df_inns