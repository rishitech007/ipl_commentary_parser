FIELDER_LOCN_QRY="""
For the following fielding positions, {}, parse the commentary and get the closest matching fielding positions. \n
For example,
Q:'T Natarajan to Shivam Dube, 1 run, a low full-toss outside off, Shivam Dube swings hard and the thick outside-edge is on the bounce, 
short third man dives to his right and stops it. CSK end at 212' \n
A: Short third man \n
\n \n
For the following query, provide the fielding position,
Q:{} \n
A:If no position can be inferred, then return None. Do not hallucinate and create your own fielding positions. 
Use only from the list of positions provided. Do not provide more than one option from the list.
"""

BOWLING_LENGTH_QRY="""
For the following ball lengths, 'good','full','short','short of good','yorker','back of','full toss', 
parse the commentary and get the closest matching bowling lengths. \n
For example,        
Q:'100th 50 + score for the king in t20 full' \n
A: full \n
\n \n
For the following query, provide the bowling length,
Q:{} \n
A:
If no position can be inferred, then return None. Do not hallucinate and create your own bowling lengths. 
Use only from the list of lengths provided and do not provide additional text. Do not provide more than one option from the list.
"""

BOWLING_LINE_QRY="""
For the following ball lines, 'outside off','on off','on leg','outside leg','on middle','wide outside off','wide outside leg', 
parse the commentary and get the closest matching bowling lines. \n
For example,        
Q:'short of length on leg' \n
A: on leg \n
\n \n
For the following query, provide the bowling lines,
Q:{} \n
A:        
If no lines can be inferred, then return None. Do not hallucinate and create your own bowling lines. 
Use only from the list of lines provided and do not provide additional text. Do not provide more than one option from the list.
"""

WICKET_QRY="""
For the following text, identify who the batsman is, if there is a fielder involved in the dismissal identify him, 
if it is a bowler involved, identify him, and also the mode of dismissal ('Run out', 'Fielder caught', 'Bowled', 'LBW', 'Caught and bowled', 'Stumping'). 
If you cannot identify the information then return none, \n \n
For example, \n
Q: "NO.250 FOR THE PROTEAN PACER IN T20s </strong></span> short of good length ball, pitching outside off stump, 
Ishan Kishan went for a flashy cut shot. But he didn't connect cleanly, the ball ballooning high in the air. 
<strong>Harpreet Brar</strong>, stationed perfectly at backward point, kept his eyes on the prize and completes an easy catch.<br/>" \n \n
A:
'batsman': 'Ishan Kishan',
'fielder involved': 'Harpreet Brar',
'bowler involved': 'None',
'mode of dismissal': 'Fielder caught'                
\n \n
For the following query, provide the information,
Q:{} \n
A:
If no information can be inferred, then return None. Return it as a JSON object. Do not hallucinate and create your own dismissal. 
Use only from the list of dismissals provided. Do not provide more than one option from the list.
"""