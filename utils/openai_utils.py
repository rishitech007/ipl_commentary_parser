import os
import getpass
from openai import OpenAI
from .prompt_instructions import FIELDER_LOCN_QRY, BOWLING_LENGTH_QRY, BOWLING_LINE_QRY, WICKET_QRY
import numpy as np
import copy
from .constants import BALL_LENGTHS, BALL_LINES, FIELDING_POSITIONS, GPT_MODEL, TEMPERATURE



def set_api_key():
    """Function to set the OpenAI API key
    """
    os.environ["OPENAI_API_KEY"] = getpass.getpass("OpenAI API Key:")


def _set_openai_client():
    client = OpenAI()
    return client

def get_fielder_locn(query):
    """Function to get fielder location from the commentary

    Args:
        query (str): Commentary data

    Returns:
        str: Field containing fielder location/scoring region
    """
    prompt=[{'role':'system',
            'content':'You are an AI assitant who parses cricket commentaries and extracts relevant information about fielding positions.'},
            {
                "role": "user",
                "content": {FIELDER_LOCN_QRY}
            }]
    prompt_new = copy.deepcopy(prompt) 
    prompt_new[1]['content']=prompt_new[1]['content'].format(','.join(FIELDING_POSITIONS),query)
    client = _set_openai_client()
    resp=client.chat.completions.create(messages=prompt_new,model=GPT_MODEL,temperature=TEMPERATURE)
    response = resp.choices[0].message.content.split('A:')[-1].strip()
    return response

def get_ball_length(query):
    """Function to get ball length from the commentary

    Args:
        query (str): Commentary data

    Returns:
        str: Field containing ball length
    """
    if query!=np.nan:
        if query.strip(' ') not in BALL_LENGTHS:
            prompt=[{'role':'system',
                    'content':'You are an AI assitant who parses cricket commentaries and extracts relevant information about bowling lengths.'},
                    {
        
                        "role": "user",
                        "content": {BOWLING_LENGTH_QRY}
                    }]
            prompt_new = copy.deepcopy(prompt) 
            prompt_new[1]['content']=prompt_new[1]['content'].format(query)
            client = _set_openai_client()
            resp=client.chat.completions.create(messages=prompt_new,model=GPT_MODEL,temperature=TEMPERATURE)
            response = resp.choices[0].message.content.split('A:')[-1].strip()
        else:
            response = query.strip(' ')
        return response
    else:
        return query
    
def get_ball_line(query):
    """Function to get ball line from the commentary

    Args:
        query (str): Commentary data

    Returns:
        str: Field containing ball line
    """
    if query!=np.nan:
        if query.strip(' ') not in BALL_LINES:
            prompt=[{'role':'system',
                    'content':'You are an AI assitant who parses cricket commentaries and extracts relevant information about bowling lengths.'},
                    {
                        "role": "user",
                        "content": {BOWLING_LINE_QRY}
                    }]
            prompt_new = copy.deepcopy(prompt) 
            prompt_new[1]['content']=prompt_new[1]['content'].format(query)
            client = _set_openai_client()
            resp=client.chat.completions.create(messages=prompt_new,model=GPT_MODEL,temperature=TEMPERATURE)
            response = resp.choices[0].message.content.split('A:')[-1].strip()
        else:
            response = query.strip(' ')
        return response
    else:
        return query


def get_wicket(query):
    """Function to get wicket dismissal from the commentary

    Args:
        query (str): Commentary data

    Returns:
        str: Fields containing dismissal
    """
    prompt=[{'role':'system',
             'content':'You are an AI assitant who parses cricket commentaries and extracts relevant information about the dismissal.'},
             {
                "role": "user",
                "content": {WICKET_QRY}
            }
            ]
    prompt_new = copy.deepcopy(prompt) 
    prompt_new[1]['content']=prompt_new[1]['content'].format(query)
    client=_set_openai_client()
    resp=client.chat.completions.create(messages=prompt_new,model=GPT_MODEL,temperature=TEMPERATURE)
    response = resp.choices[0].message.content.split('A:')[-1].strip()
    return response