import header
import ui

import os
import requests
import json
import io
import re
import math
import shutil
from queue import SimpleQueue

from collections import defaultdict
from fuzzywuzzy import fuzz
from multiprocessing.pool import ThreadPool
from bisect import bisect_left
import threading
from urllib3 import disable_warnings

CHAMPIONS = []
ITEMS = defaultdict(list)
KEYSTONES = ['6161', '6162', '6164', '6261', '6262', '6263', '6361', '6362', '6363']
RUNES = {}
SUMMONERS = {}
aliases = {'ez':'Ezreal', 'gp':'Gangplank', 'j4':'JarvanIV', 'tf':'TwistedFate', 'ww':'Warwick', 'mf':'MissFortune'}
import operator
validops = {
        '=' :operator.eq,
        '==':operator.eq,
        '!=':operator.ne,
        '<' :operator.lt,
        '>' :operator.gt,
        '<=':operator.le,
        '>=':operator.ge
        }
validfields = ["kills","deaths","assists","kd","perfectkd","team","kp","gameLength","cs","cspm","gold","largestMultiKill","ASSISTS","BARON_KILLS","BARRACKS_KILLED","BOUNTY_LEVEL","CHAMPIONS_KILLED","CHAMPION_MISSION_STAT_0","CHAMPION_MISSION_STAT_1","CHAMPION_MISSION_STAT_2","CHAMPION_MISSION_STAT_3","CHAMPION_TRANSFORM","COMBAT_PLAYER_SCORE","CONSUMABLES_PURCHASED","DOUBLE_KILLS","DRAGON_KILLS","EXP","FRIENDLY_DAMPEN_LOST","FRIENDLY_HQ_LOST","FRIENDLY_TURRET_LOST","GAME_ENDED_IN_EARLY_SURRENDER","GAME_ENDED_IN_SURRENDER","GOLD_EARNED","GOLD_SPENT","HQ_KILLED","ID","INDIVIDUAL_POSITION","ITEM0","ITEM1","ITEM2","ITEM3","ITEM4","ITEM5","ITEM6","ITEMS_PURCHASED","KEYSTONE_ID","KILLING_SPREES","LARGEST_CRITICAL_STRIKE","LARGEST_KILLING_SPREE","LARGEST_MULTI_KILL","LEVEL","LONGEST_TIME_SPENT_LIVING","MAGIC_DAMAGE_DEALT_PLAYER","MAGIC_DAMAGE_DEALT_TO_CHAMPIONS","MAGIC_DAMAGE_TAKEN","MINIONS_KILLED","MUTED_ALL","NAME","NEUTRAL_MINIONS_KILLED","NEUTRAL_MINIONS_KILLED_ENEMY_JUNGLE","NEUTRAL_MINIONS_KILLED_YOUR_JUNGLE","NODE_CAPTURE","NODE_CAPTURE_ASSIST","NODE_NEUTRALIZE","NODE_NEUTRALIZE_ASSIST","NUM_DEATHS","OBJECTIVES_STOLEN","OBJECTIVES_STOLEN_ASSISTS","OBJECTIVE_PLAYER_SCORE","PENTA_KILLS","PERK0","PERK0_VAR1","PERK0_VAR2","PERK0_VAR3","PERK1","PERK1_VAR1","PERK1_VAR2","PERK1_VAR3","PERK2","PERK2_VAR1","PERK2_VAR2","PERK2_VAR3","PERK3","PERK3_VAR1","PERK3_VAR2","PERK3_VAR3","PERK4","PERK4_VAR1","PERK4_VAR2","PERK4_VAR3","PERK5","PERK5_VAR1","PERK5_VAR2","PERK5_VAR3","PERK_PRIMARY_STYLE","PERK_SUB_STYLE","PHYSICAL_DAMAGE_DEALT_PLAYER","PHYSICAL_DAMAGE_DEALT_TO_CHAMPIONS","PHYSICAL_DAMAGE_TAKEN","PING","PLAYERS_I_MUTED","PLAYERS_THAT_MUTED_ME","PLAYER_POSITION","PLAYER_ROLE","PLAYER_SCORE_0","PLAYER_SCORE_1","PLAYER_SCORE_10","PLAYER_SCORE_11","PLAYER_SCORE_2","PLAYER_SCORE_3","PLAYER_SCORE_4","PLAYER_SCORE_5","PLAYER_SCORE_6","PLAYER_SCORE_7","PLAYER_SCORE_8","PLAYER_SCORE_9","QUADRA_KILLS","SIGHT_WARDS_BOUGHT_IN_GAME","SKIN","SPELL1_CAST","SPELL2_CAST","SPELL3_CAST","SPELL4_CAST","STAT_PERK_0","STAT_PERK_1","STAT_PERK_2","SUMMON_SPELL1_CAST","SUMMON_SPELL2_CAST","TEAM","TEAM_EARLY_SURRENDERED","TEAM_OBJECTIVE","TEAM_POSITION","TIME_CCING_OTHERS","TIME_OF_FROM_LAST_DISCONNECT","TIME_PLAYED","TIME_SPENT_DISCONNECTED","TOTAL_DAMAGE_DEALT","TOTAL_DAMAGE_DEALT_TO_BUILDINGS","TOTAL_DAMAGE_DEALT_TO_CHAMPIONS","TOTAL_DAMAGE_DEALT_TO_OBJECTIVES","TOTAL_DAMAGE_DEALT_TO_TURRETS","TOTAL_DAMAGE_SELF_MITIGATED","TOTAL_DAMAGE_SHIELDED_ON_TEAMMATES","TOTAL_DAMAGE_TAKEN","TOTAL_HEAL","TOTAL_HEAL_ON_TEAMMATES","TOTAL_PLAYER_SCORE","TOTAL_SCORE_RANK","TOTAL_TIME_CROWD_CONTROL_DEALT","TOTAL_TIME_SPENT_DEAD","TOTAL_UNITS_HEALED","TRIPLE_KILLS","TRUE_DAMAGE_DEALT_PLAYER","TRUE_DAMAGE_DEALT_TO_CHAMPIONS","TRUE_DAMAGE_TAKEN","TURRETS_KILLED","UNREAL_KILLS","VICTORY_POINT_TOTAL","VISION_SCORE","VISION_WARDS_BOUGHT_IN_GAME","WARD_KILLED","WARD_PLACED","WARD_PLACED_DETECTOR","WAS_AFK","WAS_AFK_AFTER_FAILED_SURRENDER","WAS_EARLY_SURRENDER_ACCOMPLICE","WIN"]
textfields = ["NAME","SKIN","INDIVIDUAL_POSITION", "TEAM_POSITION", "WIN"]
equivalent = {
    "Commencing Stopwatch"              :"Stopwatch",
    "Broken Stopwatch"                  :"Stopwatch",
    "Circlet of the Iron Solari"        :"Locket of the Iron Solari",
    "Forgefire Cape"                    :"Sunfire Cape",
    "Frozen Fist"                       :"Iceborn Gauntlet",
    "Infernal Mask"                     :"Abyssal Mask",
    "Luden's Pulse"                     :"Luden's Echo",
    "Might of the Ruined King"          :"Blade of the Ruined King",
    "Molten Edge"                       :"Infinity Edge",
    "Obsidian Cleaver"                  :"Black Cleaver",
    "Rabadon's Deathcrown"              :"Rabadon's Deathcap",
    "Salvation"                         :"Redemption",
    "Trinity Fusion"                    :"Trinity Force",
    "Salvation"                         :"Redemption",
    "Wooglet's Witchcrown"              :"Wooglet's Witchcap",
    "Youmuu's Wraithblade"              :"Youmuu's Ghostblade",
    "Zhonya's Paradox"                  :"Zhonya's Hourglass",
    "Archangel's Staff (Quick Charge)"  :"Archangel's Staff",
    "Manamune (Quick Charge)"           :"Manamune",
    "Rod of Ages (Quick Charge)"        :"Rod of Ages",
    "Tear of the Goddess (Quick Charge)":"Tear of the Goddess",
    "Space Vampiric Scepter"            :"Vampiric Scepter",
    "Space Bloodthirster"               :"Bloodthirster",
    "Space Knight's Vow"                :"Knight's Vow",
    "Space Hextech Gunblade"            :"Hextech Gunblade",
    "Space Blade of the Ruined King"    :"Blade of the Ruined King",
    "Space Bilgewater Cutlass"          :"Bilgewater Cutlass",
    "Space Maw of Malmortius"           :"Maw of Malmortius",
    "Space Boots of Lucidity"           :"Ionian Boots of Lucidity",
    "Space Ravenous Hydra"              :"Ravenous Hydra",
    "Space Mercurial Scimitar"          :"Mercurial Scimitar",
    "Space Death's Dance"               :"Death's Dance"
}
KEY = b''
PORT = b''


def get_match_info(queue, dic):
    if KEY == b'':
        return
    while True:
        matchid = queue.get()
        if matchid == 'DONE':
            return
        if matchid not in dic.keys():
            j = client_get('lol-match-history/v1/games/' + str(matchid))
            if j != '':
                dic[matchid] = json.loads(j)
            else:
                return

def init():
    global KEY
    global PORT

    if not os.path.isdir(header.settings["DATA_FOLDER"]):
        os.mkdir(header.settings["DATA_FOLDER"])
    
    def load_settings(path):
        l = len(header.settings['VIS'])
        try:
            with open(path, 'r') as file:
                temp = json.load(file)
                for key in header.settings.keys():
                    if key in temp:
                        header.settings[key] = temp[key]
                if len(header.settings['VIS']) != l:
                    header.settings['VIS'] = [1]*l
        except:
            return False
        return True
    
    success = load_settings(header.settings["DATA_FOLDER"] + 'settings.json')

    if header.settings['CLIENT'] and os.path.exists(header.settings["LOCKFILE_PATH"]):
        file = open(header.settings["LOCKFILE_PATH"], 'rb')
        l = file.read().split(b':')
        file.close()
        PORT = l[2].decode("utf-8") 
        KEY = l[3]
    
    if not success:
        if os.path.exists("./resources/"):
            shutil.move("./resources/", header.settings["DATA_FOLDER"]+"/resources/")
        if os.path.exists("./json/"):
            shutil.move("./json/", header.settings["DATA_FOLDER"]+"/json/")
        if KEY == b'':
            header.settings["REPLAY_FOLDER"] = (os.getenv('USERPROFILE') 
            + '/Documents/League of Legends/Replays')
        else:
            header.settings["REPLAY_FOLDER"] = client_get('lol-replays/v1/rofls/path')
            header.settings["MATCH_URL"] = client_get('lol-replays/v1/rofls/path')
        
    

def save():
    print("SAVE")
    if os.path.exists(header.settings["DATA_FOLDER"]):
        with open(header.settings["DATA_FOLDER"] + 'settings.json', 'w+') as f:
            json.dump(header.settings, f)

# connect to the league client
def client_get(url):
    session = requests.Session()
    session.verify = False
    try:
        r = session.get('https://127.0.0.1:'+PORT+'/'+url, auth=('riot', KEY))
        print(r)
        return (r.content.decode('utf-8'))
    except requests.exceptions.ConnectionError:
        ui.warn('Cannot connect to League client')
        return ""

def download_patch(patch):
    # print('download patch:',patch)
    # ui.disable_btns(patch)
    # command = ('"'+header.settings['DATA_FOLDER']+'LeagueDownloader.exe" solution -n lol_game_client_sln -o "'+
    #     header.settings['DATA_FOLDER']+str(patch)+'" -v '+str(patch))
    # os.system(command)
    pass


def download_json(patch, json_file):
    """downloads json from specific patch

    Args:
        patch (string): patch number
        json_file (string): filename.json
    """
    json_url = 'https://ddragon.leagueoflegends.com/cdn/' + \
        patch+'/data/'+header.settings["LOCALE"] + '/' + json_file
    folder = header.settings["DATA_FOLDER"] + 'json/'
    if not os.path.exists(folder):
        os.mkdir(folder)
    with open(folder + json_file, 'wb+') as file:
        try:
            file.write(requests.get(json_url).content)
        except requests.exceptions.ConnectionError:
            ui.warn('Cannot connect to cdn')

def download_images(urls, local_paths):
    """downloads urls as local_paths
    
    Args:
        urls (list): Source of images
        local_paths (list): Locations(filenames) to save images to
    """
    flag = 'xb'
    def download(data):
        try:
            with open(data[1], flag) as file:
                with requests.get(data[0], stream=True) as r:
                    shutil.copyfileobj(r.raw, file)
        except FileExistsError: return
        except requests.exceptions.ConnectionError:
            ui.warn('Cannot connect to cdn')
            return
    
    pool = ThreadPool(header.NUM_THREADS)
    result = pool.map(download, zip(urls, local_paths))
    pool.close()
    pool.join()

def download_legacy():
    data_folder = header.settings["DATA_FOLDER"]
        
    # download champion portraits
    folder = data_folder + 'legacy/champion/'
    if not os.path.exists(folder):
        os.makedirs(folder)
    
    with open(data_folder+'json/champion.json') as f:
        champs = json.load(f)
    urls, paths = ([], [])
    for c in champs:
        for i in range(len(champs[c])):
            urls.append('https://ddragon.leagueoflegends.com/cdn/%s/img/champion/%s.png'%(champs[c][i], c))
            paths.append(folder+'%s_%d.png'%(c, i))
    download_images(urls, paths)

    # download item images
    folder = data_folder + 'legacy/item/'
    if not os.path.exists(folder):
        os.makedirs(folder)

    with open(data_folder+'json/item_legacy.json') as f:
        items = json.load(f)
    urls, paths = ([], [])
    for t in items:
        for i in range(len(items[t])):
            urls.append('https://ddragon.leagueoflegends.com/cdn/%s/img/item/%s.png'%(items[t][i], t))
            paths.append(folder+'%s_%d.png'%(t, i))
    download_images(urls, paths)

    # download masteries
    folder = data_folder + 'legacy/mastery/'
    if not os.path.exists(folder):
        os.makedirs(folder)
    download_json('6.24.1', 'mastery.json')
    urls = ['https://ddragon.leagueoflegends.com/cdn/6.24.1/img/mastery/%s.png'%k for k in KEYSTONES]
    paths = [folder + k + '.png' for k in KEYSTONES]
    download_images(urls, paths)

    header.settings["LEGACY"] = False


def update():
    """downloads latest champion, item, rune, and summoner spell images
    """
    # check current patch
    try:
        url_version = 'https://ddragon.leagueoflegends.com/api/versions.json'
        version = requests.get(url_version).content.decode('utf-8')
        pos = version.find('["') + 2
        patch = version[pos:version.find('"', pos)]
    except requests.exceptions.ConnectionError:
        ui.warn('Cannot connect to cdn')
        return

    if patch != header.settings["PATCH"] or True:
        download_json(patch, 'championFull.json')
        download_json(patch, 'item.json')
        download_json(patch, 'runesReforged.json')
        download_json('9.13.1', 'summoner.json')
        build_lists()
        data_folder = header.settings["DATA_FOLDER"]
        # download champ images
        url = 'https://ddragon.leagueoflegends.com/cdn/' + patch + '/img/champion/'
        folder = data_folder + 'champion/'
        if not os.path.exists(folder):
            os.mkdir(folder)
        urls, paths = ([], [])
        for c in CHAMPIONS:
            urls.append(f'{url}{c}.png')
            paths.append(f'{folder}{c}.png')
        download_images(urls, paths)

        # download item images
        url = 'https://ddragon.leagueoflegends.com/cdn/' + patch + '/img/item/'
        folder = data_folder + 'item/'
        if not os.path.exists(folder):
            os.mkdir(folder)
        urls, paths = ([], [])
        for i in ITEMS.values():
            for j in i:
                urls.append(f'{url}{j}.png')
                paths.append(f'{folder}{j}.png')
        download_images(urls, paths)

        # download rune images
        with open(data_folder + 'json\\runesReforged.json') as file:
            rune_json = file.read()
            url = 'https://ddragon.leagueoflegends.com/cdn/img/'
            rune_urls = [url + r[7:] for r in re.findall('icon":".*?(?=")', rune_json)]
            folder = data_folder + 'rune/'
            if not os.path.exists(folder):
                os.mkdir(folder)
            download_images(rune_urls, [folder + '%d.png'%r for r in RUNES.values()])


        # download summoner spell images
        url = 'https://ddragon.leagueoflegends.com/cdn/' + '9.13.1' + '/img/spell/'
        folder = data_folder + 'legacy/summoner/'
        if not os.path.exists(folder):
            os.mkdir(folder)
        urls, paths = ([], [])
        for s in SUMMONERS.values():
            urls.append(f'{url}{s}.png')
            paths.append(f'{folder}{s}_0.png')
        download_images(urls, paths)
        print(SUMMONERS)
        header.settings["PATCH"] = patch

def parse_search(query):
    """parses query string into list of functions
    
    Args:
        query (str): query string
    
    Returns:
        list: list of boolean functions filters replays
        func: boolean function to sort replays after filtering
    """
    fun_search = []
    fun_sort = 0
    fun = 0

    query = re.sub('[^a-z0-9 .><!=]', '', query.lower())
    q = list(filter(None, query.split(' ')))
    sortpos = q.index('sort') if 'sort' in q else -2
    sort_arg = q[sortpos +
                 1] if sortpos != -2 and sortpos + 1 < len(q) else None
    search_args = [
        i for i in range(len(q)) if i != sortpos and i != sortpos + 1
    ]

    num_args = []
    other_args = []
    for a in search_args:
        other_args.append(a) if all(c not in q[a]
                                    for c in '><!=') else num_args.append(a)

    # Generates a function that
    #   returns value of arg for a given replay r
    # Returns a tuple containing that function and
    # 0 if it returns a number
    # 1 if it returns a string
    def argtofun(arg):
        if re.search('[a-zA-Z]', arg) or not len(arg):
            # argument is a field of the replay data
            m = [fuzz.token_set_ratio(arg, r) for r in validfields]
            # argument is a string
            if max(m) < 80:
                return lambda r, a=arg: a, 1
            arg = validfields[m.index(max(m))]
            if arg in textfields:
                return lambda r, a=arg: re.sub(' ','',r.get(a).lower()) if r.get(a) != None else None, 1
            else:
                return lambda r, a=arg: int(r.geta(a)), 0
        else:
            # argument is a number
            return lambda r, x=float(arg): x, 0
    
    def calc(op, a, b):
        # older replays may not have every valid field, so we need to check for None
        if a == None or b == None:
            return False
        return op(a,b)
    
    # Non-Numerical Arguments
    
    def fuzzy(token):
        rmax = 0
        fun = 0
        # TODO: Add support for summoner spells, legacy champs, legacy runes
        for k in CHAMPIONS:
            r = fuzz.token_set_ratio(token, k)
            if r > rmax:
                # print(r,k)
                rmax = r
                fun = lambda r, champ=k: r.get('SKIN') == champ
                if rmax == 100: break

        for k in ITEMS:
            r = fuzz.token_set_ratio(token, k)
            if r > rmax:
                rmax = r
                # print(k, ITEMS[k])
                fun = lambda r, items=ITEMS[k]: any([any([r.get('ITEM' + str(i)) == item for i in range(7)]) for item in items])
                if rmax == 100: break
        for k in RUNES:
            r = fuzz.token_set_ratio(token, k)
            if r > rmax:
                # print(r,k)
                rmax = r
                fun = lambda r, rune=RUNES[k]: r.get('KEYSTONE_ID') == rune
                if rmax == 100: break
        return fun

    if not num_args and not other_args:
        fun_search.append(lambda x: True)
    else:
        for a in num_args:
            op = [i for i, x in enumerate(q[a]) if x in '><!=']
            arg1 = q[a][:op[0]]
            arg2 = q[a][op[-1] + 1:]
            opstr = q[a][op[0]:op[-1] + 1]
            if opstr in validops:
                funa, istext1 = argtofun(arg1)
                funb, istext2 = argtofun(arg2)
                # if only one arg is text, args are not comparable
                if istext1 == istext2:
                    fun = lambda r, a=funa, b=funb, op=validops[opstr]: calc(op,a(r), b(r))
                    fun_search.append(fun)
                break

        for a in other_args:
            if q[a] in aliases:
                fun_search.append(
                    lambda r, champ=aliases[q[a]]: r.get('SKIN') == champ)
            else:
                fun = fuzzy(q[a])
                if fun:
                    fun_search.append(fun)

    if sort_arg != None:
        fun_sort = lambda l, ascending=sort_arg[
            -1] == '.': l.sort(key=lambda i, f=argtofun(sort_arg): f[0](header.replays[i]), reverse=ascending)

    return fun_search, fun_sort

def build_lists():
    """maps item/rune ids to names

    lists valid champ names
    """
    global CHAMPIONS
    global ITEMS
    global RUNES
    global SUMMONERS
    # run once
    if len(CHAMPIONS) and len(ITEMS):
        return

    folder = header.settings["DATA_FOLDER"] + 'json/'
    if not os.path.exists(folder):
        ui.warn(header.settings["DATA_FOLDER"] + 'json/ DNE')
        return

    if not os.path.exists(folder + 'championFull.json'):
        ui.warn(folder + 'championFull.json DNE')
    else:
        with open(folder + 'championFull.json', encoding="utf8") as file:
            s = file.read()
            CHAMPIONS = re.sub('[0-9:"{}]', '', s[s.rfind('"keys":') + 7:]).split(',')

    if not os.path.exists(folder + 'champion.json'):
        ui.warn(folder + 'champion.json DNE')
    else:
        with open(folder + 'champion.json', encoding="utf8") as file:
            ui.LEGACY_CHAMP = json.load(file)


    if not os.path.exists(folder + 'item.json'):
        ui.warn(folder + 'item.json DNE')
    else:
        with open(folder + 'item.json', encoding="utf8") as file:
            for r in re.findall('.{4}":{"name":".*?(?=")', file.read())[1:]:
                name = r[r.rfind('"') + 1:]
                if name in equivalent:
                    ITEMS[equivalent[name]].append(r[:4])
                ITEMS[name].append(r[:4])
    
    if not os.path.exists(folder + 'item_legacy.json'):
        ui.warn(folder + 'item_legacy.json DNE')
    else:
        with open(folder + 'item_legacy.json', encoding="utf8") as file:
            ui.LEGACY_ITEM = json.load(file)
            for item in ui.LEGACY_ITEM:
                if ui.LEGACY_ITEM[item]['name'] not in ITEMS.keys():
                    ITEMS[ui.LEGACY_ITEM[item]['name']] = item

    if not os.path.exists(folder + 'mastery.json'):
        ui.warn(folder + 'mastery.json DNE')
    else:
        with open(folder + 'mastery.json', encoding="utf8") as file:
            for r in re.findall('.{4},"name":".*?(?=")', file.read()):
                s = r[r.rfind('"') + 1:]
                i = bisect_left(KEYSTONES, r[:4])
                if i != len(KEYSTONES) and KEYSTONES[i] == r[:4]:
                    RUNES[s] = r[:4]

    if not os.path.exists(folder + 'runesReforged.json'):
        ui.warn(folder + 'runesReforged.json DNE')
    else:
        with open(folder + 'runesReforged.json', encoding="utf8") as file:
            rune = json.load(file)
            for i in rune:
                # rune tree
                RUNES[i['name']] = i['id']
                # keystone runes
                for r in i['slots'][0]['runes']:
                    RUNES[r['name']] = r['id']

    if not os.path.exists(folder + 'summoner.json'):
        ui.warn(folder + 'summoner.json DNE')
    else:
        with open(folder + 'summoner.json', encoding="utf8") as file:
            pos = 0
            s=file.read()
            while True:
                pos = s.find('"id":"', pos) + 6
                if pos == 5:
                    break
                name = s[pos : s.find('"',pos)]
                pos += len(name)
                pos = s.find('"key":"', pos) + 7
                if pos == 6:
                    break
                key = s[pos : s.find('"',pos)]
                pos += len(key)
                while key[0]=='f':
                    pos = s.find('"key":"', pos) + 7
                    if pos == 6:
                        break
                    key = s[pos : s.find('"',pos)]
                    pos += len(key)
                SUMMONERS[key] = name

def search(text):
    from ui import display
    fun_search, fun_sort = parse_search(text)
    prev = []
    result = [i for i in range(len(header.replays))]
    for f in fun_search:
        prev = result
        result = []
        for i in prev:
            if f(header.replays[i]):
                result.append(i)

    if fun_sort:
        print("fun sort")
        print(result)
        fun_sort(result)
        print(result)
    display(result)

def index_replays():
    """creates list of replay objects from replay files
    """
    minfopath = header.settings["DATA_FOLDER"]+'matchinfo'
    try:
        with open(minfopath, 'r') as file:
            dic = json.load(file)
    except:
        dic = {}
    q = SimpleQueue()
    t1 = threading.Thread(target=get_match_info, args=(q, dic))
    t1.start()
    for f in os.listdir(header.settings["REPLAY_FOLDER"]):
        if f.endswith('.rofl'):
            print('IS ROFL: ',f)
            filename = header.settings["REPLAY_FOLDER"] + '\\' + f
            try:
                header.replays.append(replay(filename, q))
            except:
                print('failed: ', filename)
                pass

    q.put('DONE')
    t1.join()
    header.EXTRA_INFO = dic
    with open(header.settings["DATA_FOLDER"] + 'matchinfo', 'w+') as f:
        json.dump(dic, f)
    print('finished indexing replays')

class team:
    def __init__(self, players):
        self.team = players[0]['TEAM']
        self.kills = 0
        self.deaths = 0
        self.assists = 0
        self.gold = 0
        self.inhibs = 0
        self.towers = 0
        self.barons = 0
        self.dragons = 0
        self.size = len(players)
        def get(p, field):
            if field in p:
                return p[field]
            return 0
        for p in players:
            self.kills   += int(get(p, 'CHAMPIONS_KILLED'))
            self.deaths  += int(get(p, 'NUM_DEATHS'))
            self.assists += int(get(p, 'ASSISTS'))
            self.gold    += int(get(p, 'GOLD_EARNED'))
            self.inhibs  += int(get(p, 'BARRACKS_KILLED'))
            self.towers  += int(get(p, 'TURRETS_KILLED'))
            self.barons  += max(int(get(p, 'BARON_KILLS')), int(get(p, 'SUPER_MONSTER_KILLED')))
            self.dragons += int(get(p, 'DRAGON_KILLS'))

class replay:
    """initializes replay object
    
    Args:
        filename (str): path to replay file on disk
    """
    def __init__(self, filename, queue):

        def UINT(byte):
            return int.from_bytes(byte, byteorder='little')

        try:
            data = open(filename, 'rb').read()
            # ===========  READ HEADER  ===========

            fileheader = data[262:288]
            self.filename = filename
            # headerLength        = UINT(fileheader[0:2])
            # fileLength          = UINT(fileheader[2:6])
            metaheaderOffset = UINT(fileheader[6:10])
            # metaheaderLength    = UINT(fileheader[10:14])
            payloadHeaderOffset = UINT(fileheader[14:18])
            # payloadHeaderLength = UINT(fileheader[18:22])
            self.payloadOffset = UINT(fileheader[22:26])
            print(self.payloadOffset)

            js = json.loads(data[metaheaderOffset:payloadHeaderOffset])
            self.matchId = UINT(data[payloadHeaderOffset:payloadHeaderOffset+8])

            print('matchId:', self.matchId)
            queue.put(self.matchId)

            self.gameVersion = js['gameVersion']
            self.data = json.loads(js['statsJson'])
            self.player = 0
            self.set_player(header.settings['NAME'])
            
            # ===========    STATS    ===========

            # assumes teams are guaranteed to be contiguous
            team2index = len(self.data)
            for i in range(len(self.data)):
                if self.data[i]['TEAM'] == '200':
                    team2index = i
                    break
                    
            self.team1 = team(self.data[:team2index])
            self.team2 = team(self.data[team2index:])

            self.kills = int(self.get('CHAMPIONS_KILLED'))
            self.deaths = int(self.get('NUM_DEATHS'))
            self.assists = int(self.get('ASSISTS'))
            if self.deaths == 0:
                self.kd = self.kills + self.assists
                self.perfectkd = True
            else:
                self.kd = (self.kills + self.assists) / self.deaths
                self.perfectkd = False

            self.team = self.get('TEAM')
            
            if self.team == self.team1.team:
                teamkills = self.team1.kills
            else:
                teamkills = self.team2.kills

            self.kp = math.floor(self.kills / teamkills * 100)
            self.gameLength = int(js['gameLength'])
            print('gamelength', self.gameLength)
            self.cs = int(self.get('MINIONS_KILLED'))
            self.cspm = self.cs / self.gameLength * 60000
            self.gold = int(self.get('GOLD_EARNED'))
            self.gpm = self.gold / self.gameLength * 60000
            self.largestMultiKill = int(self.get('LARGEST_MULTI_KILL'))

        except Exception as ex:
            print(type(ex).__name__, ex.args)
            raise

    def get(self, key):
        try:
            return self.data[self.player][key]
        except:
            return None

    def geta(self, key):
        result = getattr(self, key, None)
        if result == None:
            return self.get(key)
        return result

    def has(self, key):
        return key in self.data[self.player]
    
    def set_player(self, name):
        for i in range(len(self.data)):
            if self.data[i]['NAME'] == name:
                self.player = i
                break

def set_setting(value, setting):
    """sets setting to value
    
    Args:
        value (void): new value for setting
        setting (str): setting to be changed
    """
    print('set setting:', setting, value)
    header.settings[setting] = value
    if setting == 'NAME':
        name = header.settings['NAME']
        for r in header.replays:
            r.set_player(name)
    print(header.settings[setting])
