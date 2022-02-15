
import re
from stemming.porter2 import stem

sw_path = "./englishST.txt"

sw = []

with open(sw_path) as f:
    for line in f:
        sw.append(line.split('\n')[0])
        
def preprocessMultipleSongLyrics(songs, stopping=False,stemming=True):

    """
    This takes a dictionary of format {<songname> : <lyrics>}

    Returns a dictonary of format {<songname> : <preprocessed lyrics>}
    
    """
    preprocessedSongLyrics = {}

    for song in songs.keys():

        preprocessedSongLyrics[song] = preprocessSongLyrics(songs[song], stopping, stemming)

    return preprocessedSongLyrics

def preprocessSongLyrics(songLyrics,stopping=False,stemming=True):

    """
    Takes a string of lyrics line seperated by \n 

    Returns a 2D array of each line where each element array represents 
    the preprocessed word and it's overall position for that line
    
    """

    preprocessedLines = []

    pos = 0
    
    for line in songLyrics.split("\n"):
        
        tokens = re.sub("\W+", " ",line)

        caseTokens = tokens.casefold().split()

        stemmedLineTokens = []

        for word in caseTokens:
            if (word not in sw or not stopping):
                if stemming:
                    stemmedLineTokens.append((stem(word),pos)) 
                else:
                    stemmedLineTokens.append((word,pos)) 
                pos += 1
        
        if len(stemmedLineTokens) > 0:
            preprocessedLines.append(stemmedLineTokens)
    
    return preprocessedLines

