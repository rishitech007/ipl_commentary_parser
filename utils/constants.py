SCHEDULE_URL = {'iplt20':"https://www.iplt20.com/matches/results",
                'cb':'https://www.cricbuzz.com/cricket-series/7607/indian-premier-league-2024/matches'
}

RESULTS_URL = 'https://www.iplt20.com/matches/results'

TEAMS_DICT={
    'Chennai Super Kings':'CSK',
    'Mumbai Indians':'MI',
    'Punjab Kings':'PBKS',
    'Delhi Capitals':'DC',
    'Kolkata Knight Riders':'KKR',
    'Sunrisers Hyderabad':'SRH',
    'Gujarat Titans':'GT',
    'Lucknow Super Giants':'LSG',
    'Royal Challengers Bengaluru':'RCB',
    'Rajasthan Royals':'RR',
}

HOME_CITY_DICT ={
    'Chennai Super Kings': ['Chennai'],
    'Mumbai Indians': ['Mumbai'],
    'Punjab Kings':['Mullanpur','Dharamsala','Mohali'],
    'Delhi Capitals':['Delhi','Visakhapatnam'],
    'Kolkata Knight Riders': ['Kolkata'],
    'Sunrisers Hyderabad': ['Hyderabad'],
    'Gujarat Titans': ['Ahmedabad'],
    'Lucknow Super Giants': ['Lucknow'],
    'Royal Challengers Bengaluru': ['Bengaluru'],
    'Rajasthan Royals':['Jaipur','Guwahati'],
}


CB_URL = 'https://www.cricbuzz.com'


IPL_T20_DF_COLS = ['Match id','Date','Location','Home Team','Away Team','First batting','Second batting','URL']

IPL_T20_COMM_DF_COLS = ['Match ID','Team','Innings','Ball','Batsman',
                        'Bowler','Runs','Batsman runs','Boundary','Wicket','Dismissal',
                        'Wide','No ball','Bye','Leg bye','Commentary']

CB_DF_COLS =['Match id','Date','Location','Home Team','Away Team','URL']

RESULTS_COLS = ['Match id','Date','Location','Home Team','Away Team','Result']

VALID_SOURCE =['cb','iplt20']

FIRST_INNINGS = 1

IPL_T20 = 'iplt20'

CRICBUZZ = 'cb'

IPL_T20_SCHEDULE_LOCN = 'data/iplt20/schedule/'

IPL_T20_COMM_LOCN = 'data/iplt20/commentary/'

CB_SCHEDULE_LOCN ='data/cricbuzz/schedule/'

CB_COMM_LOCN = 'data/cricbuzz/commentary/'

MERGED_COMM_LOCN = 'data/merged/commentary/'

MERGED_COMM_CLEAN_LOCN = 'data/merged/commentary_clean/'

SCORES_LOCN = 'data/scores/'

SCORES_FILE = 'scores.csv'

RESULTS_LOCN = 'data/results/'

RESULTS_FILE = 'results.csv'

SCHEDULE_FILE = 'schedule.csv'

COLS_STR =['Location','Date']

COLS_TO_KEEP = ['Match id_x', 'Location', 'Home Team_x','Away Team_x','URL_x',
                'First batting','Second batting','Match id_y']


BALL_LENGTHS=['good','full','short','short of good','yorker','back of','full toss']

FIELDING_POSITIONS=['Short Third Man', 'Extra Cover', 'Forward Short Leg', 'Deep Backward Point',
                    'Deep Point','Deep Extra Cover', 'Deep Cover', 'Sweeper', 'Long Off',
                    'Long On', 'Deep Mid Wicket', 'Deep Forward Square Leg', 'Deep Square Leg',
                    'Backward Square Leg', 'Deep Backward Square Leg', 'Leg Slip', 'Short Fine Leg',
                    'Wicketkeeper', 'Third Man', 'Slips', 'Gully', 'Point', 'Cover', 'Mid-Off',
                    'Mid-On', 'Mid-Wicket', 'Square Leg', 'Fine Leg', 'Short Leg','Silly mid-on',
                    'Silly mid-off','silly point','Fly slip','Cow corner','Leg gully']

BALL_LINES=['outside off','on off','on leg','outside leg','on middle','wide outside off','wide outside leg']

GPT_MODEL='gpt-4o'

TEMPERATURE=0.1