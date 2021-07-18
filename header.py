import os
import gettext

settings = {
    "LOCKFILE_PATH"     : r'C:/Riot Games/League of Legends/lockfile',
    "LOCALE"            : 'en_US',
    "PATCH"             : '9.3.1',
    "DATA_FOLDER"       : f"{os.getenv('APPDATA')}/Replay Parser/",
    "UPDATE"            : True,
    "LEGACY"            : True,
    "REPLAY_FOLDER"     : "",
    "MATCH_URL"         : "http://matchhistory.na.leagueoflegends.com",
    "MATCH_LANGUAGE"    : "en",
    "MATCH_SERVER"      : "NA1",
    "NAME"              : "",
    "FONT_SIZE"         : "14px",
    "VERSION"           : "0.1",
    "VIS"               : [1,1,1,1,1,1,1,1,1,1,1,1,1,1,0,1,1],
    "CLIENT"            : True,
    "LANGUAGE"          : "English"
}

NUM_THREADS = 16
replays = []
EXTRA_INFO = {}
