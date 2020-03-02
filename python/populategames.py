# Import all the bits and bobs we'll need
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt 
import slippi
import time
from datetime import datetime 
import os
import sys
import matplotlib.image as mpimg 
import matplotlib
import gc
# from slippi import Game
# from slippi import Game1Frame
from slippi import Game
import json
import preprocessing as pp
import states

import pdb #debugger

global folderUrl
folderUrl = ""

#####wins and losses stats##########
myWinLoss = pp.myWinLoss
oppWinLoss = pp.oppWinLoss
myKillDeath = pp.myKillDeath
myMatchups = pp.myMatchups
all_games = pd.DataFrame(columns = ['jiggs_port', 
                                    'opp_port', 
                                    'matchup', 
                                    'stage', 
                                    # 'win', 
                                    'duration', 
                                    # 'filename',
                                    'date'])

MYWINLOSS = None
OPPWINLOSS = None
MYRATIO = None######kills and deaths stats############
MYKILLDEATH = None

MYMATCHUPSLIST = []
MYMATCHUPS = None
"""
-----------
   STATS
-----------
shortest game ?
longest game ?
number of 4 stocks, i've done X
number of 4 stocks on me X
num of deaths X
num of kills X
total w/l X
w/l for each character X
total k/d X
k/d for each character X
data over time: wins (per character too) stock graph
matchups?
"""

MyFourStocks = 0
OppFourStocks = 0
Deaths = 0
Kills = 0

def getStats(characters):
    global MyFourStocks, OppFourStocks, Deaths, Kills, game, myWinLoss, oppWinLoss #refactor countwins and losses
    try:
        countDeaths(characters)
    except AttributeError: #"'NoneType' has no attribute 'leader'"
        return False
    except ValueError:
        return False
    countWins(characters)
    countMatchups(characters)
    return True

def countWins(characters):
    global filename, wins, losses, i, game, myWinLoss, oppWinLoss
    me = pp.character_name(characters[0][1])
    opp = pp.character_name(characters[1][1])
    date = datetime.strptime(filename[5:-4], "%Y%m%dT%H%M%S")
    game.won = wonGame(game, characters[0][0], characters[1][0])
    # pdb.set_trace()
    if game.won:
        game.won = "WON"
        myWinLoss[me]["wins"] += 1
        oppWinLoss[opp]["losses"] += 1
        wins += 1
    else:
        game.won = "LOST"
        myWinLoss[me]["losses"] += 1
        oppWinLoss[opp]["wins"] += 1
        # print(f"Adding 1 loss to {me}, 1 win to {opp}")
        losses += 1
    # print(myWinLoss)
    # print(oppWinLoss)
    # print(f"{i}: {game.won} {pp.character_name(characters[0][1])} (me) vs. {pp.character_name(characters[1][1])} on {datetime.strftime(date, '%D, %T')}")

    #we don't care about dittos
    # if characters[0][1] != pp.jiggs[0] and characters[1][1] != pp.jiggs[0]:
    #     if characters[0][1] != pp.jiggs[0]:
    #         characters.reverse()
    # add_game(game, characters, filename, date)

def countDeaths(characters): # count deaths of me, add to total, count 4 stocks
    global MyFourStocks, OppFourStocks, Deaths, Kills, game
    myLastState = None
    oppLastState = None
    myDeathsThisGame = 0
    oppDeathsThisGame = 0
    for frame in game.frames:
        myState = slippi.id.ActionState(frame.ports[0].leader.post.state)
        oppState = slippi.id.ActionState(frame.ports[1].leader.post.state)
        if states.is_dead(myState): #i died
            if myState != myLastState: #check to make sure it's not duplicated
                myLastState = myState
                Deaths += 1
                myDeathsThisGame += 1
                myKillDeath[pp.character_name(frame.ports[0].leader.post.character)]["deaths"] += 1
        else:
            myLastState = None
        if states.is_dead(oppState): #opponent died
            if oppState != oppLastState: #check to make sure it's not duplicated
                oppLastState = oppState
                Kills += 1
                oppDeathsThisGame += 1
                myKillDeath[pp.character_name(frame.ports[0].leader.post.character)]["kills"] += 1
        else:
            oppLastState = None
    if myDeathsThisGame == 4 and oppDeathsThisGame == 0:
        MyFourStocks += 1
    if myDeathsThisGame == 0 and oppDeathsThisGame == 4:
        OppFourStocks += 1
    # print([myKillDeath[x] for x in myKillDeath if myKillDeath[x] and myKillDeath[x]["kills"]])

def countMatchups(characters): # count matchup wins and losses
    global myMatchups, game
    me = pp.character_name(characters[0][1])
    opp = pp.character_name(characters[1][1])
    # print(game.won)
    if game.won == "WON":
        myMatchups[me][opp]["wins"] += 1
    else:
        myMatchups[me][opp]["losses"] += 1
    # print(myMatchups[me][opp])

# Determines if i won
def wonGame(game, myPort, opp_port):
    
    # Get the last frame
    last_frame = game.frames[-1]
    
    # The post-processing result of the last frame
    j_post = last_frame.ports[myPort].leader.post
    opp_post = last_frame.ports[opp_port].leader.post
    
    # First, compare stock counts
    j_stocks = j_post.stocks
    opp_stocks = opp_post.stocks
    
    if j_stocks > opp_stocks: return True
    if j_stocks < opp_stocks: return False
    
    # If stocks are the same, compare percent
    j_dmg = j_post.damage
    opp_dmg = opp_post.damage
    
    # It's almost unheard of for both players to end at the exact same percent.
    # In this extremely unlikely event, we give the match to jiggs
    if j_dmg <= opp_dmg: return True
    else: return False

# Add a single game to our dataframe
def add_game(game, characters, fname, date):
    
    global all_games
    
    myPort = characters[0][0]
    opp_port = characters[1][0]
    
    game_data = {
        'jiggs_port': myPort,
        'opp_port': opp_port,
        'matchup': pp.character_name(opp_port),
        'stage': pp.stage_name(game.start.stage),
        'win': game.won,
        'duration': game.metadata.duration,
        # 'filename': fname,
        'date': datetime.strftime(date, '%D, %T')
    }
    
    all_games = all_games.append(game_data, ignore_index = True)

def addWinLoss():
    global myWinLoss, oppWinLoss, MYWINLOSS, OPPWINLOSS, MYRATIO

    # i = 0
    MYWINLOSS = None
    MYWINLOSS = pd.DataFrame(columns = ['character', 'wins', 'losses'])
    MYRATIO = None
    MYRATIO = pd.DataFrame(columns = ['character', 'wlRatio'])
    for key in myWinLoss:
        if myWinLoss[key]:
            if myWinLoss[key]["wins"] == 0 and myWinLoss[key]["losses"] == 0:
                continue
            data = {
                "character": key,
                "wins": myWinLoss[key]["wins"],
                "losses": myWinLoss[key]["losses"]
            }
            MYWINLOSS = MYWINLOSS.append(data, ignore_index = True)
            if myWinLoss[key]["losses"] == 0:
                myWinLoss[key]["losses"] = 1
            MYRATIO = MYRATIO.append({"character": key, "wlRatio": myWinLoss[key]["wins"] / myWinLoss[key]["losses"]}, ignore_index = True)
    OPPWINLOSS = None
    OPPWINLOSS = pd.DataFrame(columns = ['character', 'wins', 'losses'])
    for key in oppWinLoss:
        if oppWinLoss[key]["wins"] == 0 and oppWinLoss[key]["losses"] == 0:
            continue
        data = {
            "character": key,
            "wins": oppWinLoss[key]["wins"],
            "losses": oppWinLoss[key]["losses"]
        }
        OPPWINLOSS = OPPWINLOSS.append(data, ignore_index = True) #add to dataframe

def addKillDeath():
    global myKillDeath, MYKILLDEATH
    MYKILLDEATH = None
    MYKILLDEATH = pd.DataFrame(columns = ['character', 'kills', 'deaths'])
    for key in myKillDeath:
        if myKillDeath[key] and myKillDeath[key]["deaths"] > 0:
            data = {
                "character": key,
                "kills": myKillDeath[key]["kills"],
                "deaths": myKillDeath[key]["deaths"]
            }
            MYKILLDEATH = MYKILLDEATH.append(data, ignore_index = True)#add to dataframe

def addMatchups(characters=pp.all_characters):
    global myMatchups, MYMATCHUPS
    MYMATCHUPS = None
    matchupsCharacterData = {}
    MYMATCHUPS = pd.DataFrame(columns = ['character', 'wins', 'losses'])
    # print("columns: " + JSON.stringify(c))
    for me in myMatchups:
        if me != "Pichu" and me != "Bowser" and me != "Kirby" and me != "Ness" and me != "Mewtwo":
            # if me in characters:
            matchupsCharacterData[me] = []
            for opp in myMatchups[me]:
                data = {}
                # pdb.set_trace()
                # if myMatchups[me][opp]["wins"] + myMatchups[me][opp]["losses"] > 10: #if more than 100 games
                data["character"] = opp
                data["wins"] = myMatchups[me][opp]["wins"]
                data["losses"] = myMatchups[me][opp]["losses"]
                if data["wins"] > 0 or data["losses"] > 0:
                    matchupsCharacterData[me].append(data)
                # MYMATCHUPS = MYMATCHUPS.append(data, ignore_index = True)
            # print("MYMATCHUPS")
            # print(MYMATCHUPS)
    # matchupsCharacterData.append(MYMATCHUPS)
    return matchupsCharacterData

# Makes sure the game is not corrupt before returning it
def validate_game(fname):
    # print(folderUrl + "/" + fname)
    try:
        game = Game(folderUrl + "/" + fname)
        # game = Game1Frame('games/' + fname)
        return game
    except KeyboardInterrupt:
        sys.exit()
    except:
        print('Game ' + fname + ' contains corrupt data.')
        return None

def makeMeFirstPlayer(game, ports):
    global characters
    if game.myport == 0:
        if ports[0]:
            char = ports[0].leader.post.character
            characters.append((0, char))
            char = ports[1].leader.post.character
            characters.append((1, char))
    elif game.myport == 1:
        if ports[1]:
            char = ports[1].leader.post.character
            characters.append((1, char))
            char = ports[0].leader.post.character
            characters.append((0, char))
    else:
        print("3+ player game, skipping...");
        return False
    return True

def populateData(portDict, url):
    global folderUrl, myWinLoss, oppWinLoss, wins, losses, badfiles, filename, wins, losses, i, characters, game
    folderUrl = url
    # setupRecords()
    wins = 0
    losses = 0
    # print(f"myports: {myports}")
    i = 0
    badfiles = 0

    # print(myWinLoss)

    for filename in os.listdir(folderUrl):
        try:
            myport = portDict[filename] #check if filename exists in portDict
        except KeyError:
            badfiles += 1
            continue # no match found

        game = validate_game(filename) #massively slow, why?
        # game = Game1Frame('games/' + filename) #for short, quick data
        # print(game.frames[1].ports)
        if not game:
            badfiles += 1
            continue

        game.myport = myport
        del myport
        
        #First frame of the game
        try:
            frame_one = game.frames[1]
        except IndexError:
            badfiles += 1
            continue
        ports = frame_one.ports
        characters = list()

        ##### i am always first player :) #####
        try:
            if not makeMeFirstPlayer(game, ports):
                continue
        except AttributeError: #strange error, corrupted data
            badfiles += 1
            continue
        ######

        try:
            me = pp.character_name(characters[0][1])
            opp = pp.character_name(characters[1][1])
            date = datetime.strptime(filename[5:-4], "%Y%m%dT%H%M%S")
        except IndexError:
            badfiles += 1
            continue

        if not getStats(characters): #if there's an error in the game
            badfiles += 1
            continue

        i += 1
        # if i % 10 == 0: #for testing
        #     plotData()
        # printData()
        printDataForParse()
    time.sleep(1)
    print("DONE")
    plotData()
    # print(f"{badfiles} bad files found")


def plotData():
    global MYWINLOSS, OPPWINLOSS, MYRATIO, wins, losses, badfiles
    addWinLoss()
    addKillDeath()
    matchupsCharacterData = addMatchups()


    # print("plotting")
    killColors = ['b', 'black']
    winColors = ['g', 'r']
    MYWINLOSS.plot(x="character", y=["wins", "losses"], kind="bar", color=winColors).set_title("My Character\'s wins and losses")
    MYRATIO.plot(x="character", y="wlRatio", kind="bar", color=['c']).set_title("My Character\'s win/loss ratio")
    OPPWINLOSS.plot(x="character", y=["wins", "losses"], kind="bar", color=winColors[::-1]).set_title("Opponent's Character's wins and losses")
    MYKILLDEATH.plot(x="character", y=["kills", "deaths"], kind="bar", color=killColors).set_title("My Character's kills and deaths")
    
    for x in matchupsCharacterData:
        if matchupsCharacterData[x]:
            MYMATCHUPS = None
            MYMATCHUPS = pd.DataFrame(columns = ['character', 'wins', 'losses'])
            MYMATCHUPS = MYMATCHUPS.append(matchupsCharacterData[x], ignore_index = True)
            MYMATCHUPS.plot(x="character", y=["wins", "losses"], kind="bar", color=winColors).set_title(f"My {x}'s matchups")
    plt.show()


def printData():
    global myWinLoss, oppWinLoss, wins, losses, badfiles
    print()
    print()
    print(f"----{Kills} total kills----{Deaths} total deaths----{Kills/Deaths} (Ratio)----{MyFourStocks} 4stocks----{OppFourStocks} opp4stocks----")
    print()
    print("____________________________MY_WIN_LOSS_RATIO__________________________")
    for key in myWinLoss:
        if myWinLoss[key] and myWinLoss[key]["losses"]:
            print(f"{key}: {myWinLoss[key]['wins']} total wins, {myWinLoss[key]['losses']} total losses. Ratio of {myWinLoss[key]['wins'] / myWinLoss[key]['losses']}")
    print("___________________________OPP_WIN_LOSS_RATIO__________________________")
    for key in oppWinLoss:
        if oppWinLoss[key] and oppWinLoss[key]["losses"]:
            print(f"{key}: {oppWinLoss[key]['wins']} total wins, {oppWinLoss[key]['losses']} total losses. Ratio of {oppWinLoss[key]['wins'] / oppWinLoss[key]['losses']}")
    print("_______________________________________________________________________")
    print(f"{wins} total wins, {losses} total losses. Ratio of {wins/losses}")
    print("_______________________________________________________________________")

def printDataForParse():
    global myWinLoss, oppWinLoss, wins, losses, badfiles
    pData = [wins, losses, Kills, Deaths, MyFourStocks, OppFourStocks, i, badfiles]
    # pData[0] = wins
    # pData[1] = losses
    # pData[2] = Kills
    # pData[3] = Deaths
    # pData[4] = MyFourStocks
    # pData[5] = OppFourStocks
    # pData[6] = i
    # pData[7] = badfiles

    print(pData)