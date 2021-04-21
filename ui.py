import header
from other import set_setting, search, save, download_patch,\
    init, index_replays, update, build_lists, SUMMONERS, download_legacy

import os
import subprocess
import math
import webbrowser
from functools import lru_cache
from enum import Enum
from abc import ABC, abstractmethod

from PyQt5.QtWidgets import QApplication, QLabel, QDialog, QVBoxLayout,\
     QHBoxLayout, QLineEdit, QGraphicsOpacityEffect, QWidget, QStackedLayout,\
     QGridLayout, QScrollArea, QGraphicsRotation, QSizePolicy, QSpacerItem
from PyQt5.QtCore import QByteArray, Qt, pyqtSignal, QRectF, QRect, QSize,\
    QPoint, QPointF, QVariantAnimation, QAbstractAnimation, QThread
from PyQt5.QtGui import QColor, QPixmap, QPainter, QImage, QBrush, QTransform

from matplotlib import rc, pyplot
from matplotlib.figure import Figure
from matplotlib.transforms import Bbox, TransformedBbox
from matplotlib.backends.backend_qt4agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt4agg import NavigationToolbar2QT as NavigationToolbar
import numpy as np

SCALE = 0.5
WARNING_WIDGET = []
warnings = []
warning_visible = False
qw_result = 0
current_search = 0
stylesheets = {}

LEGACY_CHAMP = {}
LEGACY_ITEM = {}
downloaded_patches = []
downloading_patch = ""
dlbtns = []
_ = lambda s:s

class VIS(Enum):
    CHAMP = 0
    RUNES = 1
    SUMMS = 2
    ITEMS = 3
    POS = 4
    WIN = 5
    KDA = 6
    KD = 7
    KP = 8
    CS = 9
    CSM = 10
    GOLD = 11
    GOLDM = 12
    MULTIK = 13
    DLBTN = 14
    TEAMS = 15
    TIME = 16

class qcolors:
    #blues
    light_border= QColor(9,   230, 215)
    dark_border = QColor(31,  123, 190)
    light_bg    = QColor(16,  48,  96)
    bg          = QColor(16,  32,  64)
    #bg= QColor(1,10,19)
    win         = QColor(10,  200, 230)
    #yellows    
    yellow      = QColor(250, 190, 10)
    ico         = QColor(205, 190, 145)
    ico_hover   = QColor(240, 230, 210)
    item        = QColor(203, 170, 100)
    item_dark   = QColor(70,  55,  20)
    gray        = QColor(150, 150, 130)
    #reds
    loss        = QColor(255, 35,  69)
    black       = QColor(0,   0,   0)

class color:
    #blues
    light_border= "rgb(9,210,200)"
    med_border  = "rgb(27,140,195)"
    dark_border = "rgb(31,123,190)"
    light_bg    = "#103060"
    med_bg      = "#102245"
    bg          = "#102040"
    dark_bg     = "rgb(0,10,20)"
    #bg= "rgb(1,10,19)"
    win         = "rgb(10,200,230)"
    #yellows    
    yellow      = "rgb(250,190,10)"
    ico         = "rgb(205,190,145)"
    ico_hover   = "rgb(240,230,210)"
    item        = "rgb(203,170,100)"
    item_med    = "rgb(120,90,40)"
    item_dark   = "rgb(70,55,20)"
    gray        = "rgb(150,150,130)"
    #reds
    loss        = "rgb(255,35,69)"

class fsize:
    font_size="25"
    stats_font_size="25"
    name_font_size="20"
    kda_font_size="40"
    win_font_size="25"
    padding="20"


def get_style(name):
    """Returns Qt Style Sheet (must call make_styles first)
    
    Args:
        name (str): name of style
    
    Returns:
        str: style sheet
    """
    try:
        return stylesheets[name]()
    except KeyError:
        return ""
def make_styles():
    """fills dict stylesheets with functions
    
    Returns:
        None
    """
    def inactive():
        return ("*{"
            "font-size:" + str(int(int(fsize.font_size) * SCALE)) + 'px;' +
            "border-style: solid;"
            "border-width: 1px;" + "padding: 3px; padding-right:" + fsize.padding +
            "px;"
            "border-color:" + color.dark_border + ';'
            "background:" + color.bg + ';'
        "}"
        "*:hover{"
            "border-color:" + color.med_border+';'
            "background:" + color.med_bg + ";"
        "}"
        "*:focus{"
            "border-color:" + color.med_border +
            "qlineargradient(x1:0, y1:0, x2:0, y2:1, stop: 0 " +
            color.med_border + ", stop: 1 " + color.light_border + ")" +
            color.light_border +
            "qlineargradient(x1:0, y1:0, x2:0, y2:1, stop: 0 " +
            color.med_border + ", stop: 1 " + color.light_border +
            ");" + "background:"
            "qlineargradient(x1:0, y1:0, x2:0, y2:1, stop: 0 " +
            color.light_bg + ", stop: 1 " + color.med_bg + ");"
        "}")
    def active():
        return ("*{"
        "font-size:" + str(int(int(fsize.font_size) * SCALE)) + 'px;' +
        "border-style: solid;"
        "border-width: 1px;" + "padding-right: " + fsize.padding +
        "px;"
        "border-color:" + color.light_border +
        "qlineargradient(x1:0, y1:0, x2:0, y2:1, stop: 0 " +
        color.light_border + ", stop: 1 " + color.dark_border + ")" +
        color.dark_border +
        "qlineargradient(x1:0, y1:0, x2:0, y2:1, stop: 0 " +
        color.light_border + ", stop: 1 " + color.dark_border +
        ");" + "background:"
        "qlineargradient(x1:0, y1:0, x2:0, y2:1, stop: 0 " +
        color.light_bg + ", stop: 1 " + color.bg + ");"
        "}")
    def main():
        return ("*{"
            "font-size:" + str(int(int(fsize.font_size) * SCALE)) + 'px;' +
            "color:" + color.item + ";"
            "background:" + color.bg + ';' + 
            "border: 0px;" 
        "}"
        "QMenu{"
            "border-width: 1px;"
            "border-style: solid;"
            "padding: 3px;"
            "border-color:" + color.dark_border +";"
        "}"
        "QMenu::item:selected{"
            "background:" + color.light_bg +";"
        "}"
        "QScrollBar:vertical {"
            "border: 0px;"
			"border-radius: 5px;"
            "background-color:"+color.dark_bg+";"
            "width:10px;" 
            "margin: 0px 0px 0px 0px;"
        "}"
        "QScrollBar::handle:vertical {"
          	"border: 0px;"
			"border-radius: 5px;"
			"background-color:"+color.item_med+";"
        "}"
        "QScrollBar::handle:vertical:hover {"
			"background-color:"+color.item+";"
        "}"
        "QScrollBar::handle:vertical:pressed {"
			"background-color:"+color.item_dark+";"
        "}"
        "QScrollBar:horizontal{ height: 0px; }"
        "QScrollBar::add-line:vertical { border: none; background: none; }"
        "QScrollBar::sub-line:vertical { border: none; background: none; }"
        "QScrollBar::add-page:vertical { background: none; }"
        "QScrollBar::sub-page:vertical { background: none; }")
    def itempic0():
        return ("*{"
        "border-style: solid;"
        "border-width: 1px;"
        "border-color:" + color.item + ";"
        "}")
    def itempic():
        return ("*{"
        "border-style: solid;"
        "border-width: 1px 1px 1px 0;"
        "border-color:" + color.item + ";"
        "}")
    def info():
        return ("*{"
        "font-family: 'Segoe UI';" + "font-size:" +
        str(int(int(fsize.stats_font_size) * SCALE)) + 'px;' + "color:" + 
        color.item + ';' + "}")
    def info_hover():
        return ("*{"
        "font-family: 'Segoe UI';" + "font-size:" +
        str(int(int(fsize.stats_font_size) * SCALE)) + 'px;' + "color:" +
        color.ico + ';' + "}")
    def stats():
        return ("*{"
        "font-family: 'Segoe UI';"
        "font-size:" + str(int(int(fsize.stats_font_size) * SCALE)) + 'px;'
        "color:" + color.ico + ';' + "font-weight:bold;" + "}")
    def stats_hover():
        return ("*{"
        "font-family: 'Segoe UI';"
        "font-size:" + str(int(int(fsize.stats_font_size) * SCALE)) + 'px;'
        "color:" + color.ico_hover + ';' + "font-weight:bold;" + "}")
    def scoreboard():
        return ("*{"
        "font-family: 'Segoe UI';"
        "font-size:" + str(int(int(fsize.stats_font_size) * SCALE)) + 'px;'
        "color:" + color.ico_hover + ';' + "font-weight:900;" + "}")
    def scoreboard_yellow():
        return ("*{"
        "font-family: 'Segoe UI';"
        "font-size:" + str(int(int(fsize.stats_font_size) * SCALE)) + 'px;'
        "color:" + color.yellow + ';' + "font-weight:900;" + "}")
    def name_yellow():
        return ("*{"
        "font-family: 'Segoe UI';"
        "font-size:" + str(int(int(fsize.name_font_size) * SCALE)) + 'px;'
        "color:" + color.yellow + ';' + "font-weight:bold;" + "}")
    def name_gray():
        return ("*{"
        "font-family: 'Segoe UI';"
        "font-size:" + str(int(int(fsize.name_font_size) * SCALE)) + 'px;'
        "color:" + color.gray + ';' + "font-weight:bold;" + "}")
    def win():
        return ("*{"
        "font-family: 'Segoe UI';"
        "font-size:" + str(int(int(fsize.win_font_size) * SCALE)) + 'px;'
        "color:" + color.win + ';' + "font-weight:bold;" + "}")
    def loss():
        return ("*{"
        "font-family: 'Segoe UI';"
        "font-size:" + str(int(int(fsize.win_font_size) * SCALE)) + 'px;'
        "color:" + color.loss + ';' + "font-weight:bold;" + "}")
    def kda():
        return ("*{"
        "font-family: 'Segoe UI';"
        "font-size:" + str(int(int(fsize.kda_font_size) * SCALE)) + 'px;'
        "color:" + color.ico + ';' + "font-weight:bold;" + "}")
    def kda_hover():
        return ("*{"
        "font-family: 'Segoe UI';"
        "font-size:" + str(int(int(fsize.kda_font_size) * SCALE)) + 'px;'
        "color:" + color.ico_hover + ';' + "font-weight:bold;" + "}")
    stylesheets['inactive'] = inactive
    stylesheets['active'] = active
    stylesheets['main'] = main
    stylesheets['itempic0'] = itempic0
    stylesheets['itempic'] = itempic
    stylesheets['info'] = info
    stylesheets['info-hover'] = info_hover
    stylesheets['stats'] = stats
    stylesheets['stats-hover'] = stats_hover
    stylesheets['scoreboard'] = scoreboard
    stylesheets['scoreboard-yellow'] = scoreboard_yellow
    stylesheets['name-yellow'] = name_yellow
    stylesheets['name-gray'] = name_gray
    stylesheets['win'] = win
    stylesheets['loss'] = loss
    stylesheets['kda'] = kda
    stylesheets['kda-hover'] = kda_hover

# returns QPixmap displaying scaled resource
def get_scaled_resource(string, w=0, h=0):
    if h == 0:
        return makeimg(header.settings["DATA_FOLDER"]+'resources/' + string + '.png', w, w)
    return makeimg(header.settings["DATA_FOLDER"]+'resources/' + string + '.png', w, h)

def get_resource(string):
    """returns QPixmap of resource
    
    Args:
        string (str): filename
    
    Returns:
        QPixmap: requested resource, or 0 if it does not exist
    """
    # print('get_resource')
    path = header.settings["DATA_FOLDER"]+'resources/' + string + '.png'
    if os.path.exists(path):
        return QPixCache(path)

    print('resource %s does not exist'%string)
    return 0

def get_qimg_resource(string):
    path = header.settings["DATA_FOLDER"]+'resources/' + string + '.png'
    if os.path.exists(path):
        return QImgCache(path)
    print('resource %s does not exist'%string)
    return 0


@lru_cache(maxsize=100)
def QPixCache(path):
    """Caches calls to QPixmap
    
    Args:
        path (str): path to image
    
    Returns:
        QPixmap: image
    """
    return QPixmap(path)

@lru_cache(maxsize=32)
def QImgCache(path):
    """Caches calls to QImage
    
    Args:
        path (str): path to image
    
    Returns:
        QImage: image
    """
    return QImage(path)


def warn(name, args=None):
    class warning:
        def __init__(self, name, args):
            self.name = name
            if args:
                self.argstr = str(args[0])
                for arg in args[1:]:
                    self.argstr += " | " + arg
            else:
                self.argstr = ''

    # print('ECHO WARNING: ', name, args)
    warnings.append(warning(name, args))
    if len(WARNING_WIDGET) != 0:
        if not warning_visible:
            WARNING_WIDGET[0].show()
            WARNING_WIDGET[0].clicked.connect(
                lambda: WARNING_WIDGET[1].setVisible(
                    not WARNING_WIDGET[1].isVisible())
                )
        for warning in warnings:
            WARNING_WIDGET[1].setText(WARNING_WIDGET[1].text() + 
                warning.name + ': ' + warning.argstr + '\n')


def thousands_separator(string):
    """Adds thousands separator to number strings
    
    Args:
        string (str): Number (9000)
    
    Returns:
        str: Number (9,000)
    """
    string2 = ''
    if header.settings["LOCALE"] == 'en_US':
        sep = ','
    else:
        sep = '.'
    while len(string) > 3:
        string2 = string[-3:] + sep + string2
        string = string[:-3]
    string2 = string + sep + string2
    string2 = string2[:-1]
    return string2

def get_blank_img(width, height=0):
    """blank pixmap
    
    Args:
        width (int): width
        height (int): height. Defaults to 0.
    
    Returns:
        QPixmap: blank pixmap
    """
    if height == 0:
        height = width
    pix = QPixmap(width, height)
    pix.fill(Qt.transparent)
    return pix

def get_colored_rect(qcolor, width, height):
    """Pixmap of colored rectangle
    
    Args:
        qcolor (QColor): color
        width (int): width
        height (int): height
    
    Returns:
        QPixmap: Pixmap of colored rectangle
    """
    pix = QPixmap(width, height)
    pix.fill(qcolor)
    return pix

def readable_time(ms):
    """Converts ms to mm:ss / hh:mm:ss
    
    Args:
        ms (int): milliseconds
    
    Returns:
        str: readable time
    """
    s = math.floor((ms / 1000) % 60)
    m = math.floor((ms / 60000) % 60)
    h = math.floor(ms / 3600000)
    if h > 0:
        return str(h) + ':' + str(m) + ':' + str(s)
    else:
        return str(m) + ':' + str(s)

class trimg(QLabel):
    """QLabel with three(or two) pixmaps
    
    Args:
        normal (QPixmap): normal color
        light (QPixmap): light color
        dark (QPixmap, optional): dark color. Defaults to 0.
    """
    def __init__(self, normal, light, dark=0):
        super(QLabel, self).__init__(PARENTPTR)
        self.img = normal
        self.hover = light
        self.click = dark
        self.normalize()

    def normalize(self):
        self.setPixmap(self.img)

    def brighten(self):
        self.setPixmap(self.hover)

    def darken(self):
        if self.click:
            self.setPixmap(self.click)

def lighten(img, mask=False):
    """Lightens images
    
    Args:
        img (QPixmap): image
    
    Returns:
        QPixmap: lighter image
    """
    try:
        pix = get_blank_img(img.width(), img.height())
        painter = QPainter(pix)
        painter.drawPixmap(QRectF(img.rect()), img, QRectF(img.rect()))
        painter.setCompositionMode(QPainter.CompositionMode_Overlay)
        overlay = get_colored_rect(QColor(255, 255, 255, 128), img.width(),
                                   img.height())
        painter.drawPixmap(QRectF(overlay.rect()), overlay,
                           QRectF(overlay.rect()))
        painter.end()
        if mask:
            pix2 = get_blank_img(img.width(), img.height())
            painter = QPainter(pix2)
            painter.drawPixmap(QRectF(img.rect()), img, QRectF(img.rect()))
            painter.setCompositionMode(QPainter.CompositionMode_SourceIn)
            painter.drawPixmap(QRectF(pix.rect()), pix, QRectF(pix.rect()))
            painter.end()
            pix = pix2
        return pix
    except Exception as ex:
        print(type(ex).__name__, ex.args)

def circular_border(img, crop, size, width, color):
    """Adds border to circular image
    
    Args:
        img (QPixmap): Image to make circular
        crop (int): Crops pixels before masking
        size (int): Final size of image + border
        width (int): Border width
        color (QColor): Border color
    Returns:
        QPixmap: image with border
    """
    image = circular_img(img, crop, size-width*2)
    pix = get_blank_img(size)
    painter = QPainter(pix)
    painter.setRenderHint(QPainter.Antialiasing)
    painter.setPen(Qt.NoPen)
    painter.setBrush(QBrush(color, Qt.SolidPattern))
    painter.drawEllipse(pix.rect())
    painter.drawPixmap(QRectF(image.rect().adjusted(width, width, width, width)),
                                                    image, QRectF(image.rect()))
    painter.end()
    return pix

def colored_circle(img, diameter, color, text):
    """Adds level circle for champ portrait
    
    Args:
        img (QPixmap): Image to add circle to
        diameter (int): Circle diameter
        color (QColor): Circle color
        text (str): Circle text
    Returns:
        QPixmap: image with circle
    """
    blank = get_blank_img(img.width()+10*SCALE, img.height())
    painter = QPainter(blank)
    painter.drawPixmap(QRectF(img.rect()), img, QRectF(img.rect()))
    painter.setRenderHint(QPainter.Antialiasing)
    painter.setPen(Qt.NoPen)
    painter.setBrush(QBrush(color, Qt.SolidPattern))
    r = blank.rect()
    r.setTopLeft(QPoint(r.width()-diameter,r.height()-diameter))
    painter.drawEllipse(r)

    r.translate(0, -2*SCALE)
    painter.setPen(qcolors.gray)
    painter.drawText(r, Qt.AlignCenter, text)
    painter.end()
    return blank

def circular_img(img, crop, size):
    """Makes image circular
    
    Args:
        img (QPixmap): Image to make circular
        crop (int): Crops pixels before masking
        size (int): Size to scale circle
    Returns:
        QPixmap: circular image
    """
    delta = min(img.width(), img.height()) - 2 * crop
    rect = QRect((img.width() - delta) / 2, (img.height() - delta) / 2, delta, delta)
    img = img.copy(rect)
    if size != img.width():
        img = img.scaled(size, size, Qt.KeepAspectRatio, Qt.SmoothTransformation)
    pix = get_blank_img(size)
    painter = QPainter(pix)
    painter.setRenderHint(QPainter.Antialiasing)
    painter.setPen(Qt.NoPen)
    painter.setBrush(QBrush(img))
    painter.drawEllipse(0, 0, size, size)
    painter.end()
    return pix


def display(searchresult):
    """Displays search result in main window
    
    Args:
        searchresult (list): list of replay indices
    """
    if len(searchresult) == 0:
        print('SEARCH RESULT EMPTY')
        return
    global pages, runesReforged, tv, qw_result, current_search
    current_search = searchresult
    # for r in searchresult:
    try:
        qw = QWidget()
        # first search
        if not qw_result:
            qsa = QScrollArea()
            qsa.horizontalScrollBar().setEnabled(False)
            qsa.setWidgetResizable(True)
            pages[0].addWidget(qsa)
            qw_result = qsa
        else:
            qw_result.widget().setParent(None)
        
        qw_result.setWidget(qw)
        lo_vert = QVBoxLayout(qw)
        longest = 0
        for i in searchresult:
            r = header.replays[i]

            def num_digits(n):
                r = 1
                if n >= 100:
                    r += 2
                    n /= 100
                if n >= 10:
                    r += 1
                return r

            length = num_digits(r.kills)+num_digits(r.deaths)+num_digits(r.assists)
            if length > longest:
                longest = length

        for i in searchresult:
            replay_widget = replay_layout(header.replays[i], longest)
            replay_widget.clicked.connect(lambda i=i: display_match(i))
            lo_vert.addWidget(replay_widget)


        # print('6')
    except Exception as ex:
        print(type(ex).__name__, ex.args)

def replay_layout(r, longest):
    """Generates 'match history'-like banner for a replay
    
    Args:
        r (replay): the replay to display
        longest (int): the number of digits in the longest KDA
    """
    try:
        lowidget = collectionBtn()

        outerlayout = QVBoxLayout(lowidget)
        layout = QHBoxLayout()
        lo_portrait = QStackedLayout()

        lo_summrunes = QVBoxLayout()
        lo_summs = QHBoxLayout()

        qw_midinfo = QWidget(PARENTPTR)
        lo_midinfo = QVBoxLayout(qw_midinfo)

        lo_multipos = QVBoxLayout()

        lo_itemstats = QVBoxLayout()
        qw_loitems = QWidget(PARENTPTR)
        lo_items = QHBoxLayout(qw_loitems)
        lo_stats = QHBoxLayout()
        lo_kd = QHBoxLayout()
        lo_cs = QHBoxLayout()
        lo_gold = QHBoxLayout()

        lo_endstats = QVBoxLayout()
        lo_team1 = QGridLayout()
        lo_team2 = QGridLayout()
        lo_button = QVBoxLayout()

        # returns qlabel containing str after applying style
        def qltext(str, style = 'stats'):
            q = QLabel(str, PARENTPTR)
            q.setStyleSheet(get_style(style))
            lowidget.append(q, style)
            return q
        
        print('replay layout1')
        if header.settings['VIS'][VIS.CHAMP.value]:
            champIcon = get_champ_img(r.get('SKIN'), r.gameVersion)
            circle = circular_img(champIcon, 10, 120*SCALE)
            lightcircle = circular_img(lighten(champIcon), 10, 120*SCALE)
            circle = colored_circle(circle, 40*SCALE, qcolors.black, r.get('LEVEL'))
            lightcircle = colored_circle(lightcircle, 40*SCALE, qcolors.black, r.get('LEVEL'))

            qlchamp = trimg(circle, lightcircle)
            lowidget.append(qlchamp)
            lo_portrait.addWidget(qlchamp)
            

        lo_summrunes.addSpacing(30*SCALE)

        if header.settings['VIS'][VIS.RUNES.value]:
            lo_runes = QVBoxLayout()
            keystone_width = 60
            secondary_width = 40
            height = 55
            flag1 = Qt.AlignCenter
            flag2 = Qt.AlignCenter
            if header.settings['VIS'][VIS.SUMMS.value]: 
                lo_runes = QHBoxLayout()
                flag1 = Qt.AlignRight | Qt.AlignBottom
                flag2 = Qt.AlignLeft
            rune_key_img = get_rune_img(r.get('KEYSTONE_ID'), keystone_width * SCALE, keystone_width * SCALE)
            rune_key = trimg(rune_key_img, lighten(rune_key_img, True))
            if r.has('PERK_SUB_STYLE'):
                rune_sub_img = get_rune_img(r.get('PERK_SUB_STYLE'), secondary_width * SCALE, secondary_width * SCALE)
                rune_sub = trimg(rune_sub_img, lighten(rune_sub_img, True))
                rune_sub.setFixedHeight(height * SCALE)
                lo_runes.addWidget(rune_key, 0, flag1)
                lo_runes.addWidget(rune_sub, 0, flag2)
                lowidget.append(rune_sub)
            else:
                lo_runes.addWidget(rune_key, 0, Qt.AlignCenter)

            lowidget.append(rune_key)
            lo_runes.setSpacing(0)
            lo_summrunes.addLayout(lo_runes)

        print('1.3')
        if header.settings['VIS'][VIS.SUMMS.value]:
            print('summs')
            id1 = 35
            id2 = 35
            if r.matchId in header.EXTRA_INFO.keys():
                for i in range(len(header.EXTRA_INFO[r.matchId]['participantIdentities'])):
                    if header.EXTRA_INFO[r.matchId]['participantIdentities'][i]['player']['summonerName'] == header.settings['NAME']:
                        p = header.EXTRA_INFO[r.matchId]['participants'][i]
                        break
                id1 = p['spell1Id']
                id2 = p['spell2Id']

            summimg1 = get_summoner_img(id1, 50 * SCALE, 50 * SCALE)
            summIcon = trimg(summimg1, lighten(summimg1))
            summimg2 = get_summoner_img(id2, 50 * SCALE, 50 * SCALE)
            summIcon2 = trimg(summimg2, lighten(summimg2))

            lo_summs.addWidget(summIcon, 0, Qt.AlignRight | Qt.AlignTop)
            lo_summs.addWidget(summIcon2, 0, Qt.AlignLeft | Qt.AlignTop)
            lowidget.append(summIcon)
            lowidget.append(summIcon2)
            lo_summs.setSpacing(0)
            lo_summrunes.addLayout(lo_summs)
        lo_summrunes.setSpacing(0)

        print('1.4')
        if header.settings['VIS'][VIS.KDA.value]:
            lo_wrap = QHBoxLayout()
            kda = qltext(
                r.get('CHAMPIONS_KILLED') + ' / ' + r.get('NUM_DEATHS') +
                ' / ' + r.get('ASSISTS'), 'kda')
            
            q = QLabel('M'*longest, PARENTPTR)
            q.setStyleSheet(get_style('kda'))
            longest = q.sizeHint().width()
            q.deleteLater()

            x = (longest - kda.sizeHint().width())/2
            lo_wrap.addSpacing(x)
            lo_wrap.addWidget(kda, 0, Qt.AlignCenter)
            lo_wrap.addSpacing(x)
            
            lo_midinfo.addLayout(lo_wrap, Qt.AlignCenter)
        
        if header.settings['VIS'][VIS.WIN.value]:
            if r.get('WIN') == 'Win':
                qlwin = QLabel('VICTORY', PARENTPTR)
                qlwin.setStyleSheet(get_style('win'))
            else:
                qlwin = QLabel('DEFEAT', PARENTPTR)
                qlwin.setStyleSheet(get_style('loss'))
            qlwin.setFixedWidth(qlwin.sizeHint().width())
            lo_midinfo.addWidget(qlwin, 0, Qt.AlignCenter)
            lo_midinfo.addSpacing(5*SCALE)

        multipos_empty = True
        if header.settings['VIS'][VIS.MULTIK.value]:
            multipos_empty = False
            k = r.largestMultiKill
            MKSIZE = 80 * SCALE
            if (k > 0):
                qp = get_scaled_resource('ka'+str(k), MKSIZE)
                qlmk = trimg(qp, lighten(qp, True))
                lowidget.append(qlmk)
                if header.settings['VIS'][VIS.POS.value] and r.has('TEAM_POSITION'):
                    lo_multipos.addSpacing(10 * SCALE)
                lo_multipos.addWidget(qlmk, 0, Qt.AlignCenter)
        
        if header.settings['VIS'][VIS.POS.value] and r.has('TEAM_POSITION'):
            multipos_empty = False
            if len(r.get('TEAM_POSITION')):
                position = trimg(
                    get_scaled_resource(
                        r.get('TEAM_POSITION').lower(), 50 * SCALE),
                    get_scaled_resource(
                        r.get('TEAM_POSITION').lower() + '-hover', 50 * SCALE))

                lo_multipos.addWidget(position, 0, Qt.AlignCenter)
                lowidget.append(position)
        
        if multipos_empty:
            ql = QLabel(PARENTPTR)
            ql.setPixmap(get_blank_img(50))
            lo_multipos.addWidget(ql)
        lo_multipos.setSpacing(0)

        print('2')

        if header.settings['VIS'][VIS.ITEMS.value]:
            def qlitem(num, style):
                item = r.get('ITEM' + str(num))
                if item == '0':
                    ql = trimg(
                        get_blank_img(60 * SCALE, 60 * SCALE),
                        get_blank_img(60 * SCALE, 60 * SCALE))
                else:
                    ql = trimg(
                        get_item_img(item, r.gameVersion, 60 * SCALE, 60 * SCALE),
                        lighten(get_item_img(item, r.gameVersion, 60 * SCALE, 60 * SCALE)))
                ql.setStyleSheet(get_style(style))
                
                lo_items.addWidget(ql)
                lowidget.append(ql)

            qlitem(0,'itempic0')
            for i in range(1, 7):
                qlitem(i,'itempic')

            lo_items.setSpacing(0)

        print('3')
        lo_items.setSizeConstraint(QHBoxLayout.SetMinimumSize)
        lo_items_width = 60 * 7 * SCALE + 8
        if header.settings['VIS'][VIS.KD.value] or header.settings['VIS'][VIS.KP.value]:

            if r.perfectkd:
                kdstr = '%.2f' % r.kd + ':0'
            else:
                kdstr = '%.2f' % r.kd + ':1'

            kpstr = str(r.kp) + '%'

            if not header.settings['VIS'][VIS.KD.value]:
                kdstr = kpstr
            elif header.settings['VIS'][VIS.KP.value]:
                kdstr += ' (' + kpstr + ')'

            qlkd = qltext(kdstr)
            qlkd.setFixedWidth(qlkd.sizeHint().width())
            icokda = trimg(get_scaled_resource('ico-kda', 25 * SCALE),
                           get_scaled_resource('ico-kda-hover', 25 * SCALE))
            icokda.setContentsMargins(0, 5 * SCALE, 0, 0)
            lo_kd.addWidget(qlkd, 0)
            lo_kd.addWidget(icokda, 0)
            lowidget.append(icokda)
            lo_kd.setSpacing(0)
            lo_stats.addLayout(lo_kd)

        if header.settings['VIS'][VIS.CS.value] or header.settings['VIS'][VIS.CSM.value]:
            if not header.settings['VIS'][VIS.CSM.value]:
                csstr = thousands_separator(r.get('MINIONS_KILLED'))
            elif not header.settings['VIS'][VIS.CS.value]:
                csstr = '%.1f' % r.cspm
            else:
                csstr = thousands_separator(
                    r.get('MINIONS_KILLED')) + ' (' + '%.1f' % r.cspm + ')'
            qlcs = qltext(csstr)
            qlcs.setMinimumSize(qlcs.sizeHint())
            qlcs.setFixedWidth(qlcs.sizeHint().width())
            icocs = trimg(get_scaled_resource('ico-cs', 25 * SCALE),
                          get_scaled_resource('ico-cs-hover', 25 * SCALE))
            
            icocs.setContentsMargins(0, 5 * SCALE, 0, 0)
            lo_cs.addWidget(qlcs, 0)
            lo_cs.addWidget(icocs, 0)
            lowidget.append(icocs)
            lo_stats.addLayout(lo_cs)

        lo_gold_width = 0
        if header.settings['VIS'][VIS.GOLD.value] or header.settings['VIS'][VIS.GOLDM.value]:
            if not header.settings['VIS'][VIS.GOLDM.value]:
                goldstr = thousands_separator(r.get('GOLD_EARNED'))
            elif not header.settings['VIS'][VIS.GOLD.value]:
                csstr = '%.1f' % r.gpm
            else:
                goldstr = thousands_separator(
                    r.get('GOLD_EARNED')) + ' (' + '%.1f' % r.gpm + ')'
            
            gold = qltext(goldstr)
            gold.setFixedWidth(gold.sizeHint().width())
            icogold = trimg(get_scaled_resource('ico-gold', 25 * SCALE),
                            get_scaled_resource('ico-gold-hover', 25 * SCALE))
            
            icogold.setContentsMargins(0, 5 * SCALE, 0, 0)
            lo_gold.addWidget(gold, 0)
            lo_gold.addWidget(icogold, 0)
            lowidget.append(icogold)
            lo_stats.addLayout(lo_gold)
            lo_gold_width = gold.sizeHint().width() + 25 * SCALE
            lo_stats.addSpacing(1)

        lo_stats.setSpacing(0)
        lo_itemstats.addWidget(qw_loitems)
        lo_itemstats.addLayout(lo_stats, Qt.AlignBottom)
        lo_itemstats.addSpacing(10)


        print('3.5')
        print(len(header.settings['VIS']), VIS.TEAMS.value)
        if header.settings['VIS'][VIS.TEAMS.value]:
            y = 0
            for p in r.data:
                champ = QLabel(PARENTPTR)
                if p['NAME'] == header.settings['NAME']:
                    print('MASKING')
                    champ.setPixmap(circular_img(get_champ_img(p['SKIN'], r.gameVersion), 10, 25 * SCALE))
                    style = 'stats'
                else:
                    champ.setPixmap(get_champ_img(p['SKIN'],r.gameVersion ,25 * SCALE, 25 * SCALE))
                    style = 'info'
                name = qltext(p['NAME'],style)
                print(name.sizeHint().width())
                width = 200 * SCALE
                if name.sizeHint().width() > width:
                    for i in range(1, 4):
                        name = qltext(p['NAME'][:-i]+'…', style)
                        if name.sizeHint().width() < width:
                            break

                name.setFixedWidth(width)
                if p['TEAM'] == '100':
                    lo_team1.addWidget(champ, y, 0)
                    lo_team1.addWidget(name, y, 1, Qt.AlignLeft)
                    # lo_team1.setColumnStretch(2, 1)
                else:
                    lo_team2.addWidget(champ, y, 0)
                    lo_team2.addWidget(name, y, 1, Qt.AlignLeft)
                y += 1
            lo_team1.setSpacing(0)
            lo_team2.setSpacing(0)

        # 'https://ddragon.leagueoflegends.com/cdn/img/'+
        # 'LARGEST_MULTI_KILL'
        # 'KEYSTONE_ID'
        # 'PERK0'
        # 'PERK_PRIMARY_STYLE'
        # 'PERK_SUB_STYLE'

        print('4')
        if header.settings['VIS'][VIS.TIME.value]:
            qltime = qltext(readable_time(r.gameLength))
            lo_endstats.addWidget(qltime)
            patchno = r.gameVersion
            # dotpos = patchno.find('.')
            # patchno = patchno[:patchno.find('.', dotpos + 1)]
            qlpatch = qltext(patchno)
            lo_endstats.addWidget(qlpatch)

        if header.settings['VIS'][VIS.DLBTN.value]:
            dlbtn = button()
            dlbtn.clicked.connect(lambda v=r.gameVersion:download_patch(v))
            dlbtn.setIco('download', 80 * SCALE)
            playbtn = button()
            playbtn.setIco('play', 80 * SCALE)
            disabled = QLabel(PARENTPTR)
            disabled.setPixmap(get_scaled_resource('play-disabled', 80 * SCALE))
            loading = spinning_img(get_scaled_resource('play-loading', 80 * SCALE), 3000)


            lo_button.addWidget(dlbtn)
            lo_button.addWidget(playbtn)
            lo_button.addWidget(disabled)
            lo_button.addWidget(loading)
            dlbtn.hide()
            playbtn.hide()
            disabled.hide()
            loading.hide()

            if downloading_patch != "":
                if downloading_patch == r.gameVersion:
                    loading.show()
                else:
                    disabled.show()
            else:
                if r.gameVersion in downloaded_patches:
                    playbtn.show()
                else:
                    dlbtn.show()

            btntab = tab(lambda s:s.show(), lambda s:s.hide())
            btntab.append(dlbtn)
            btntab.append(playbtn)
            btntab.append(disabled)
            btntab.append(loading)
            dlbtns.append((btntab, r.gameVersion))

        print('5')
        if (r.get('WIN') == 'Win'):
            rcolor = qcolors.win
        else:
            rcolor = qcolors.loss
        midrect = QLabel(PARENTPTR)
        midrect.setPixmap(get_colored_rect(rcolor, 35 * SCALE, 150 * SCALE))
        layout.addWidget(midrect)

        # ARRANGE LAYOUT
        # region
        layout.addSpacing(30 * SCALE)
        layout.addLayout(lo_portrait)
        layout.addSpacing(10 * SCALE)
        layout.addLayout(lo_summrunes, Qt.AlignLeft)
        layout.addSpacing(10 * SCALE)
        layout.addWidget(qw_midinfo, 0, Qt.AlignLeft)
        layout.addSpacing(10 * SCALE)
        layout.addLayout(lo_multipos, Qt.AlignLeft)
        # layout.addSpacing(30 * SCALE)
        layout.addLayout(lo_itemstats, Qt.AlignLeft)
        # layout.addSpacing(50 * SCALE)
        layout.addLayout(lo_team1, Qt.AlignLeft)
        # layout.addSpacing(20 * SCALE)
        layout.addLayout(lo_team2, Qt.AlignLeft)
        # layout.addSpacing(20 * SCALE)
        layout.addLayout(lo_endstats)
        layout.addLayout(lo_button)
        layout.setSpacing(0)
        # endregion

        toprect = QLabel(PARENTPTR)
        toprect.setPixmap(get_colored_rect(rcolor, 35 * SCALE, 20 * SCALE))
        botrect = QLabel(PARENTPTR)
        botrect.setPixmap(get_colored_rect(rcolor, 35 * SCALE, 20 * SCALE))
        outerlayout.addWidget(toprect, Qt.AlignBottom)
        outerlayout.addLayout(layout)
        outerlayout.addWidget(botrect, Qt.AlignTop)
        outerlayout.setSpacing(0)
        lowidget.setFixedHeight(225*SCALE)
    except Exception as ex:
        print(type(ex).__name__, ex.args)
    print('replay_layout returned')
    return lowidget

def disable_btns(patch):
    downloading_patch = patch
    for b in dlbtns:
        if b[1] == patch:
            b[0].switchto(3)
        else:
            b[0].switchto(2)

def enable_btns():
    downloading_patch = ""
    for b in dlbtns:
        if b[1] in downloaded_patches:
            b[0].switchto(1)
        else:
            b[0].switchto(0)

def make_scoreboard(r):
    """Makes a scoreboard
    
    Args:
        r (replay): the replay
    
    Returns:
        QGridLayout: the scoreboard
    """
    logrid = QGridLayout()

    def itembar(player, patch):
        top = QVBoxLayout()
        lo = QHBoxLayout()
        ITEMSIZE = 50
        def qlitem(num, style):
            item = player['ITEM' + str(num)]
            ql = QLabel()
            if item == '0':
                ql.setPixmap(get_blank_img(ITEMSIZE * SCALE, ITEMSIZE * SCALE))
            else:
                ql.setPixmap(get_item_img(item, patch, ITEMSIZE * SCALE, ITEMSIZE * SCALE))
            ql.setStyleSheet(get_style(style))
            ql.setFixedWidth(ITEMSIZE*SCALE)
            lo.addWidget(ql)
        qlitem(0, 'itempic0')
        for i in range(1,7):
            qlitem(i, 'itempic')
        lo.setSpacing(0)
        # lo.setSizeConstraint(QHBoxLayout.SetMinimumWidth)
        top.addStretch(1)
        top.addLayout(lo)
        top.addStretch(1)
        return top
    
    t = 1
    divpos = 0
    
    names = []
    if r.matchId in header.EXTRA_INFO.keys():
        names = [p['player']['summonerName'] for p in header.EXTRA_INFO[r.matchId]['participantIdentities']]
    # make row of scoreboard
    for i in range(len(r.data)):
        p = r.data[i]
        if t == 1 and p['TEAM'] == '200':
            t = 2
            divpos = i+1
        if p['NAME'] == r.get('NAME'):
            style = get_style('scoreboard-yellow')
            namestyle = get_style('name-yellow')
            border_color = qcolors.yellow
            border_width = 2
        else:
            style = get_style('scoreboard')
            namestyle = get_style('name-gray')
            border_color = qcolors.item
            border_width = 1
        
        x = 0
        def add_widget(qw, alignment=Qt.AlignmentFlag()):
            nonlocal x
            logrid.addWidget(qw, i + t, x, alignment = alignment)
            x += 1
        def add_item(qi, alignment=Qt.AlignmentFlag()):
            nonlocal x
            logrid.addItem(qi, i + t, x, alignment = alignment)
            x += 1

        # keystone rune img
        qlrune = QLabel()
        qlrune.setPixmap(get_rune_img(p['KEYSTONE_ID'], 50 * SCALE, 50 * SCALE))
        add_widget(qlrune)

        #summoner spells
        if len(names):
            player = header.EXTRA_INFO[r.matchId]['participants'][names.index(p['NAME'])]
            losumm = QVBoxLayout()
            summ1 = QLabel()
            summ1.setPixmap(get_summoner_img(player['spell1Id'], 25 * SCALE, 25 * SCALE))
            summ2 = QLabel()
            summ2.setPixmap(get_summoner_img(player['spell2Id'], 25 * SCALE, 25 * SCALE))
            losumm.addWidget(summ1)
            losumm.addWidget(summ2)
            logrid.addLayout(losumm, i + t, x, Qt.AlignRight)
            logrid.setColumnMinimumWidth(i + 1, 40*SCALE)
            x += 1
        else:
            add_widget(QLabel())


        # level
        qlvl = QLabel(' '+p['LEVEL']+'  ')
        qlvl.setStyleSheet(style)
        add_widget(qlvl)

        # champ img
        qlchamp = QLabel()
        qlchamp.setPixmap(circular_border(get_champ_img(p['SKIN'], r.gameVersion), 10, 50 * SCALE, border_width, border_color))
        add_widget(qlchamp)

        # player name
        qlvl = QLabel('  '+p['NAME']+'   ')
        qlvl.setStyleSheet(namestyle)
        add_widget(qlvl)

        # items
        logrid.addLayout(itembar(p, r.gameVersion), i + t, x)
        x += 1

        # kda
        add_item(QSpacerItem(10, 0))
        qlkills = QLabel(p['CHAMPIONS_KILLED'])
        qldiv1 = QLabel('/')
        qldeaths = QLabel(p['NUM_DEATHS'])
        qldiv2 = QLabel('/')
        qlassists = QLabel(p['ASSISTS'])
        qlkills.setStyleSheet(style)
        qldeaths.setStyleSheet(style)
        qlassists.setStyleSheet(style)
        qldiv1.setStyleSheet(style)
        qldiv2.setStyleSheet(style)
        add_widget(qlkills, Qt.AlignCenter)
        add_widget(qldiv1, Qt.AlignCenter)
        add_widget(qldeaths, Qt.AlignCenter)
        add_widget(qldiv2, Qt.AlignCenter)
        add_widget(qlassists, Qt.AlignCenter)
        x += 1

        # cs
        add_item(QSpacerItem(10, 0))
        qlcs = QLabel(p['MINIONS_KILLED'])
        qlcs.setStyleSheet(style)
        add_widget(qlcs, Qt.AlignCenter)
        x += 1

        # gold
        add_item(QSpacerItem(10, 0))
        qlgold = QLabel(thousands_separator(p['GOLD_EARNED']))
        qlgold.setStyleSheet(style)
        add_widget(qlgold, Qt.AlignRight)

    # team label
    def tableheader(teamno, ypos):
        qlteam = QLabel('TEAM '+str(teamno))
        qlteam.setStyleSheet(get_style('stats'))
        
        if teamno == 1:
            team = r.team1
        else:
            team = r.team2

        # team kda
        lokda = QHBoxLayout()
        icokda = QLabel()
        icokda.setPixmap(get_scaled_resource('ico-kda', 25 * SCALE))
        qlkda = QLabel(str(team.kills)+' / '+str(team.deaths)+' / '+str(team.assists))
        qlkda.setStyleSheet(get_style('stats'))
        lokda.addWidget(qlkda)
        lokda.addWidget(icokda, Qt.AlignVCenter)

        # team gold
        logold = QHBoxLayout()
        icog = QLabel()
        icog.setPixmap(get_scaled_resource('ico-gold', 25 * SCALE))
        qlgold = QLabel(thousands_separator(str(team.gold)))
        qlgold.setStyleSheet(get_style('stats'))
        logold.addWidget(qlgold)
        logold.addWidget(icog)

        # icon labels
        icokd = QLabel()
        icokd.setPixmap(get_scaled_resource('ico-kda', 25 * SCALE))
        icocs = QLabel()
        icocs.setPixmap(get_scaled_resource('ico-cs', 25 * SCALE))
        icogold = QLabel()
        icogold.setPixmap(get_scaled_resource('ico-gold', 25 * SCALE))

        logrid.addWidget(qlteam, ypos, 0, 1, 0)
        logrid.addLayout(lokda, ypos, 4)
        logrid.addLayout(logold, ypos, 5, Qt.AlignCenter)
        logrid.addWidget(icokd, ypos, 9, Qt.AlignCenter)
        logrid.addWidget(icocs, ypos, 14, Qt.AlignCenter)
        logrid.addWidget(icogold, ypos, 17, Qt.AlignCenter)

    # spacing between kda, cs, and gold columns
    logrid.addWidget(QLabel('   '), 0, 8)
    logrid.addWidget(QLabel('    '), 0, 10)

    tableheader(1, 0)
    tableheader(2, divpos)

    logrid.setHorizontalSpacing(0)
    return logrid

# def make_stats(r):

def display_match(replay_index):
    """Displays info about a single match
    
    Args:
        replay_index (int): index of replay to be displayed
    """

    global TOP_LAYOUT
    global PARENTPTR

    r = header.replays[replay_index]

    layout = QVBoxLayout()

    backBtn = button()
    backBtn.setIco('x')
    backBtn.setsize(30)
    layout.addWidget(backBtn)

    tabs = tab(lambda s:s.show(), lambda s:s.hide())
    tabtn = tab(lambda s:None, lambda s:s.unpress())
    lotab = QHBoxLayout()
    layout.addLayout(lotab)
    def newtab(title):
        qw = QWidget(PARENTPTR)
        hblotab = QHBoxLayout(qw)
        qwtitle = textbutton(title, get_style('stats'), get_style('stats-hover'), istab=True)
        qwtitle.clicked.connect(lambda x=len(tabs):tabs.switchto(x))
        qwtitle.clicked.connect(lambda x=len(tabs):tabtn.switchto(x))
        lotab.addWidget(qwtitle)
        tabs.append(qw)
        tabtn.append(qwtitle)
        layout.addWidget(qw)
        qw.hide()
        return hblotab
    
    loscore = newtab('SCOREBOARD')
    lograph = newtab('GRAPHS')
    tabtn[0].press()
    tabs[0].show()

    # SCOREBOARD
    # region
    loscore.addStretch(1)
    loscore.addLayout(make_scoreboard(r))
    loobj = QVBoxLayout()
    def objective_grid(team):
        qlobj = QLabel('     OBJECTIVES', PARENTPTR)
        loico = QGridLayout()
        def addico(name, num, offset):
            ico = QLabel(PARENTPTR)
            ico.setPixmap(get_scaled_resource(name, 30 * SCALE))
            n = QLabel(str(num), PARENTPTR)
            n.setStyleSheet(get_style('scoreboard'))
            loico.addWidget(ico, 0, offset, Qt.AlignCenter)
            loico.addWidget(n, 1, offset, Qt.AlignCenter)
        
        addico('obj-tower', team.towers, 0)
        addico('obj-inhib', team.inhibs, 1)
        addico('obj-baron', team.barons, 2)
        addico('obj-dragon', team.dragons, 3)
        loobj.addWidget(qlobj)
        loobj.addLayout(loico)

    qlweb = textbutton("View on the web ↗", get_style("stats"), get_style("stats-hover"))
    qlweb.clicked.connect(lambda: webbrowser.open_new_tab(header.settings["MATCH_URL"]+'/'+
        header.settings["MATCH_LANGUAGE"]+"/#match-details/"+header.settings["MATCH_SERVER"]+
        '/'+ str(r.matchId)+'/'+str(r.get('ID'))+"?tab=overview"))
    loobj.addWidget(qlweb)

    qlfolder = textbutton("Show in folder", get_style("stats"), get_style("stats-hover"))
    qlfolder.clicked.connect(lambda: subprocess.Popen('explorer /select, "'+r.filename+'"'))
    print(r.filename)
    loobj.addWidget(qlfolder)

    objective_grid(r.team1)
    loobj.addStretch(1)
    # loobj.addSpacing(50*SCALE)
    objective_grid(r.team2)
    loobj.addStretch(1)
    loscore.addLayout(loobj)
    loscore.addStretch(1)
    # endregion

    rg = replay_graph(r)
    lov = QVBoxLayout()

    # stretch = spacing ratio of 
    # [start, between portraits, end]
    stretch = [5,4,6]
    if len(r.data) <= 6:
        stretch = [3, 7, 5]

    lov.addStretch(stretch[0])
    for i in range(len(r.data)-1, -1, -1):
        if r.data[i]['NAME'] == r.get('NAME'):
            color = qcolors.yellow
        else:
            if i < r.team2.size:
                color = qcolors.loss
            else:
                color = qcolors.win

        qlchamp = QLabel(PARENTPTR)
        qlchamp.setPixmap(circular_border(get_champ_img(r.data[i]['SKIN'], r.gameVersion), 10, 50 * SCALE, 1, color))
        lov.addWidget(qlchamp, stretch[1])
    lov.addStretch(stretch[2])
 
    lov.setSpacing(0)
    lograph.addLayout(lov)
    lograph.addWidget(rg.canvas)
    lograph.setStretchFactor(rg.canvas, 1)

    qsa = QScrollArea()
    qsa.horizontalScrollBar().setEnabled(False)
    categories = [("DAMAGE DEALT TO CHAMPIONS", ["Total Damage to Champions", "Physical Damage to Champions", "Magic Damage to Champions", "True Damage to Champions"]),
        ("TOTAL DAMAGE DEALT", ["Total Damage Dealt", "Physical Damage Dealt", "Magic Damage Dealt", "True Damage Dealt"]),
        ("DAMAGE TAKEN AND HEALED", ["Healing Done", "Damage Taken", "Physical Damage Taken", "Magic Damage Taken", "True Damage Taken", "Self Mitigated Damage"]),
        ("INCOME", ["Gold Earned", "Gold Spent"]),
        ("VISION", ["Vision Score", "Wards Placed", "Wards Destroyed", "Control Wards Purchased"]),
        ("NEUTRAL MONSTERS AND MINIONS", ["Minions Killed", "Neutral Monsters Killed", "Neutral Monsters Killed in Team Jungle", "Neutral Monsters Killed in Enemy Jungle"]),

        ("HEALING AND SHIELDING", ['Total Damage Shielded On Teammates', 'Total Heal', 'Total Heal On Teammates', 'Total Units Healed']),
        ("KDA", ['Champions Killed', 'Deaths', 'Assists', 'Largest Killing Spree', 'Killing Sprees', 'Largest Multi Kill', ]),
        ("MULTIKILLS", ['Double Kills', 'Triple Kills', 'Quadra Kills', 'Penta Kills', 'Unreal Kills', ]),
        ("OBJECTIVE DAMAGE", ['Total Damage Dealt To Objectives', 'Total Damage Dealt To Buildings', 'Total Damage Dealt To Turrets']),
        ("OBJECTIVES", ['Turrets Killed', 'Inhibitors Killed', 'Nexuses Killed', 'Baron Kills', 'Dragon Kills', 'Objectives Stolen', 'Objectives Stolen Assists', 'Node Captures', 'Node Capture Assists', 'Nodes Neutralized', 'Node Neutralize Assists', ]),
        ("SPELL CASTS", ['Spell 1 Casts', 'Spell 2 Casts', 'Spell 3 Casts', 'Spell 4 Casts', 'Summoner Spell 1 Casts', 'Summoner Spell 2 Casts']),
        ("TIME", ['Longest Time Spent Living', 'Total Time Spent Dead', 'Time CCing Others', 'Time Played', 'Time Spent Disconnected', 'Time Since Last Disconnect'])
        ]
    
    keys = ['TOTAL_DAMAGE_DEALT_TO_CHAMPIONS','PHYSICAL_DAMAGE_DEALT_TO_CHAMPIONS','MAGIC_DAMAGE_DEALT_TO_CHAMPIONS','TRUE_DAMAGE_DEALT_TO_CHAMPIONS',
        'TOTAL_DAMAGE_DEALT','PHYSICAL_DAMAGE_DEALT_PLAYER','MAGIC_DAMAGE_DEALT_PLAYER','TRUE_DAMAGE_DEALT_PLAYER',
        'TOTAL_HEAL', 'TOTAL_DAMAGE_TAKEN','PHYSICAL_DAMAGE_TAKEN','MAGIC_DAMAGE_TAKEN','TRUE_DAMAGE_TAKEN','TOTAL_DAMAGE_SELF_MITIGATED',
        'GOLD_EARNED','GOLD_SPENT',
        'VISION_SCORE','WARD_PLACED','WARD_KILLED','VISION_WARDS_BOUGHT_IN_GAME',
        'MINIONS_KILLED', 'NEUTRAL_MINIONS_KILLED', 'NEUTRAL_MINIONS_KILLED_YOUR_JUNGLE','NEUTRAL_MINIONS_KILLED_ENEMY_JUNGLE',

        'TOTAL_DAMAGE_SHIELDED_ON_TEAMMATES', 'TOTAL_HEAL', 'TOTAL_HEAL_ON_TEAMMATES', 'TOTAL_UNITS_HEALED',
        'CHAMPIONS_KILLED', 'DEATHS', 'ASSISTS', 'LARGEST_KILLING_SPREE', 'KILLING_SPREES', 'LARGEST_MULTI_KILL', 
        'DOUBLE_KILLS', 'TRIPLE_KILLS', 'QUADRA_KILLS', 'PENTA_KILLS', 'UNREAL_KILLS', 
        'TOTAL_DAMAGE_DEALT_TO_OBJECTIVES', 'TOTAL_DAMAGE_DEALT_TO_BUILDINGS', 'TOTAL_DAMAGE_DEALT_TO_TURRETS',
        'TURRETS_KILLED', 'BARRACKS_KILLED', 'HQ_KILLED', 'BARON_KILLS', 'DRAGON_KILLS', 'OBJECTIVES_STOLEN', 'OBJECTIVES_STOLEN_ASSISTS', 'NODE_CAPTURE', 'NODE_CAPTURE_ASSIST', 'NODE_NEUTRALIZE', 'NODE_NEUTRALIZE_ASSIST', 
        'SPELL1_CAST', 'SPELL2_CAST', 'SPELL3_CAST', 'SPELL4_CAST', 'SUMMON_SPELL1_CAST', 'SUMMON_SPELL2_CAST',
        'LONGEST_TIME_SPENT_LIVING', 'TOTAL_TIME_SPENT_DEAD', 'TIME_CCING_OTHERS', 'TIME_PLAYED', 'TIME_SPENT_DISCONNECTED', 'TIME_OF_FROM_LAST_DISCONNECT']
    
    # cull missing categories
    newcat = []
    newkeys = []
    nl_keys = []
    index = 0
    for c in categories:
        temp = []
        for f in c[1]:
            if keys[index] in r.data[0]:
                temp.append(f)
                nl_keys.append(f)
                newkeys.append(keys[index])
            index += 1
        if len(temp):
            newcat.append((c[0], temp))
    categories = newcat
    keys = newkeys

    def update_graph(states, replay_graph, keys):
        fields = []
        names = []
        for i in range(len(states)):
            if states[i]:
                fields.append(keys[i])
                names.append(nl_keys[i])
        replay_graph.fields(fields, names)
    
    cbt = checkbtn_tree(categories, (lambda state, rg=rg, k=keys: update_graph(state, rg, k)))
    cbt.set_state([1]+[0]*(len(nl_keys)-1))
    qsa.setWidget(cbt.qwbuttons)
    qsa.setWidgetResizable(True)
    qsa.setMinimumWidth(cbt.qwbuttons.sizeHint().width())
    lograph.addWidget(qsa)

    TOP_LAYOUT.addLayout(layout)

    def goback(layout):
        pages[0].parentWidget().show()
        clear_layout(layout)

    backBtn.clicked.connect(lambda: goback(layout))

    pages[0].parentWidget().hide()

class replay_graph():
    def __init__(self, replay):
        self.fig = Figure()
        self.fig.patch.set_facecolor(color.bg)

        self.ax = self.fig.add_subplot(111)
        self.ax.set_axisbelow(True)
        self.ax.get_yaxis().set_visible(False)
        self.ax.set_facecolor(color.bg)

        self.fig.tight_layout(pad=0, rect=(-0.01,0.04,0.92,0.93))
        
        self.canvas = FigureCanvas(self.fig)
        self.canvas.mpl_connect('motion_notify_event', self.onpick)
        self.replay = replay
        # gap between two teams
        self.ypos = [i for i in range(len(replay.data))]
        # ypos = [i for i in range(r.team1.size)] + [i for i in range(r.team1.size+1, len(r.data)+1)]
        # different colored bars for each team
        self.t1 = replay.team1.size
        self.t2 = replay.team2.size
        self.blue = ['#1BA9BD', '#098C9E', '#06535D', '#04434A']
        self.red = ['#ec2040', '#be1e37', '#8c1728', '#721220']
        self.fields(['TOTAL_DAMAGE_DEALT_TO_CHAMPIONS'], ['Total Damage to Champions'])
    
    def fields(self, field_names, names):
        data = []
        self.names = names
        for f in field_names:
            temp_arr = []
            try:
                for player in self.replay.data:
                    temp_arr.append(int(player[f]))
            except KeyError:
                temp_arr = [0]*len(self.replay.data)
            data.append(temp_arr)
        self.plot(data)

    def plot(self, data):
        width = 0.15
        spacing = 0.2
        if len(data) == 1:
            width = 0.75
            spacing = 0.25
        if len(data) == 2:
            width = 0.3
            spacing = 0.4
        elif len(data) == 3:
            width = 0.2
            spacing = 0.25
        elif len(data) == 4:
            width = 0.15
            spacing = 0.2
        
        self.ax.clear()
        self.ax.grid(True, axis='x', color='#063B45')
        self.annotations = []
        self.barchart = tab(
            lambda s, f=self: [a.set_visible(True) for a in f.annotations[s[1]]] and f.ax.set_title(''),
            lambda s, f=self: [a.set_visible(False) for a in f.annotations[s[1]]] and f.ax.set_title(''), -1)

        for i in range(min(len(data), 6)):
            print("data len", i)
            print(data[i])
            invi = len(data)-i-1
            ci = i%4
            bar = self.ax.barh([p + spacing*invi for p in self.ypos], data[i], width,
                color = [self.red[ci]]*self.t1+[self.blue[ci]]*self.t2)

            temp = []
            for rect in bar:
                height = rect.get_height()
                temp.append( 
                    self.ax.annotate('{}'.format(rect.get_width()),
                    xy=(rect.get_x() + rect.get_width(), rect.get_y() + height/2),
                    xytext=(0, 0), textcoords="offset points",
                    ha='left', va='center'))
                temp[-1].set_visible(False)
            self.annotations.append(temp)
            self.barchart.append((bar, i))

        print(self.barchart)

        # self.ax.axes.yaxis.set_ticklabels([])
        # self.ax.axes.get_yaxis().set_visible(False)
        pyplot.margins(y=0)
        self.canvas.draw()

    def onpick(self, event):
        for i in range(len(self.barchart)):
            for rect in self.barchart[i][0]:
                if rect.contains(event)[0]:
                    self.barchart.switchto(i)
                    self.ax.set_title(self.names[i])
                    self.canvas.draw()
                    return
        self.barchart.switchto(-1)
        self.canvas.draw()

class checkbtn_tree():
    def __init__(self, categories, onclick = 0):
        BUTTON_SIZE = 20*SCALE
        self.qwbuttons = QWidget(PARENTPTR)
        lobuttons = QVBoxLayout(self.qwbuttons)
        
        self.categoryButtons = []
        self.numFields = 0
        for c in range(len(categories)):
            collapseBtn = bistateBtn()
            collapseBtn.setIco('closed', 'open', BUTTON_SIZE)
            collapseBtn.setFixedSize(BUTTON_SIZE, BUTTON_SIZE)
            categoryBtn = bistateBtn()
            categoryBtn.setIco('check', 'ccheck', BUTTON_SIZE, categories[c][0], 'stats')
            lohbox = QHBoxLayout()
            lohbox.setAlignment(Qt.AlignLeft)
            lohbox.addWidget(collapseBtn)
            lohbox.addWidget(categoryBtn)
            lobuttons.addLayout(lohbox)
            self.categoryButtons.append((categoryBtn, []))
            self.numFields += len(categories[c][1])

            for f in range(len(categories[c][1])):
                b = bistateBtn()
                b.setIco('check', 'ccheck', BUTTON_SIZE, categories[c][1][f], 'stats')
                b.lo.insertSpacing(0, BUTTON_SIZE+lohbox.spacing())
                lobuttons.addWidget(b)
                b.hide()
                b.clicked.connect(lambda c=c, f=f: self.change_state(c, f))
                if onclick:
                    b.clicked.connect(lambda s=self:onclick(s.get_state()))
                self.categoryButtons[c][1].append(b)

            collapseBtn.clicked.connect(lambda fields=self.categoryButtons[c][1], cb=collapseBtn:
                [f.show() for f in fields] if cb.state else [f.hide() for f in fields])
                
            categoryBtn.clicked.connect(lambda c=c: self.change_state(c))
            if onclick:
                categoryBtn.clicked.connect(lambda s=self:onclick(s.get_state()))
        
        lobuttons.setAlignment(Qt.AlignTop)

    def get_state(self):
        return [f.state for c in self.categoryButtons for f in c[1]]
    
    def set_state(self, state):
        if len(state) != self.numFields:
            warn('set_state wrong size')
        i = 0
        for c in self.categoryButtons:
            c[0].off()
            for f in c[1]:
                f.on() if state[i] else f.off()
                i += 1
                if f.state:
                    c[0].on()

    def change_state(self, category, field=None):
        OFF = 0
        ON = 1
        cat = self.categoryButtons[category]

        # turns category and corresponding fields on or off
        def toggle_cat(cat, on):
            if on:
                cat[0].on()
                for f in cat[1]:
                    f.on()
            else:
                cat[0].off()
                for f in cat[1]:
                    f.off()

        # button is a category
        if field==None:
            # button was on, is now off
            if cat[0].state == OFF:
                toggle_cat(cat, 0)

            # button was off, is now on
            else:
                # avoid extra call to toggle_cat
                cat[0].state = OFF
                # turn off all other categories/fields
                for c in self.categoryButtons:
                    if c[0].state == ON:
                        toggle_cat(c, 0)

                toggle_cat(cat, 1)

        # button is a field
        else:
            # button was on, is now off
            if cat[1][field].state == OFF:
                all_off = True
                for f in cat[1]:
                    if f.state == ON:
                        all_off = False
                        break

                if all_off:
                    cat[0].off()

            # button was off, is now on
            else:
                cat[0].on()
                cat[1][field].on()


def clear_layout(layout):
    """deletes QLayout and children
    
    Args:
        layout (QLayout): layout to be destroyed
    """
    while layout.count():
        child = layout.takeAt(0)
        if child.widget():
            child.widget().setParent(None)
        elif child.layout():
            clear_layout(child.layout())

def get_rune_img(runeID, width=0, height=0):
    """gets keystone rune image
    
    Args:
        runeID (str): 4 digit number starting with 6 or 8
        width (int, optional): Scales output. Defaults to 0.
        height (int, optional): Scales output. Defaults to 0.
    
    Returns:
        QPixmap: width x height rune image
    """
    if int(runeID[0]) < 8:
        url = header.settings["DATA_FOLDER"] + 'legacy/rune/' + runeID + '.png'
        if os.path.isfile(url):
            return makeimg(url, width, height)
    else:
        url = header.settings["DATA_FOLDER"] + 'rune/' + runeID + '.png'
        if os.path.isfile(url):
            return makeimg(url, width, height)
            
    return get_scaled_resource('rune', width, height)

def patch_lte(a, b):
    """compares value of two patches

    Args:
        a (str): patch no 1
        b (str): patch no 2

    Returns:
        bool: true if a <= b
    """
    va = a.split(".")
    vb = b.split(".")
    for i in range(min(len(va), len(vb))):
        r = int(va[i]) - int(vb[i])
        if r < 0:
            return True
        if r > 0:
            return False
    return True

def get_champ_img(name, patch, width=0, height=0):
    """gets champion icon
    
    Args:
        name (str): Champion name
        patch (str): patch no.
        width (int, optional): Scales output. Defaults to 0.
        height (int, optional): Scales output. Defaults to 0.
    
    Returns:
        QPixmap: width x height champion icon
    """
    index = -1
    if name in LEGACY_CHAMP.keys():
        for i in reversed(range(len(LEGACY_CHAMP[name]))):
            if patch_lte(patch, LEGACY_CHAMP[name][i]):
                index = i
            else:
                break

    if index > -1:
        url = header.settings["DATA_FOLDER"] + 'legacy/champion/' + name + '_%s.png' % index
    else:
        url = header.settings["DATA_FOLDER"] + 'champion/' + name + '.png'
    
    if os.path.isfile(url):
        return makeimg(url, width, height)
    return get_scaled_resource('champ', width, height)


def get_item_img(name, patch, width=0, height=0):
    """gets item icon
    
    Args:
        name (str): item name
        patch (str): patch number
        width (int, optional): Scales output. Defaults to 0.
        height (int, optional): Scales output. Defaults to 0.
        patch (st)
    
    Returns:
        QPixmap: width x height item icon
    """
    index = -1
    if name in LEGACY_ITEM.keys():
        for i in reversed(range(len(LEGACY_ITEM[name]))):
            if patch_lte(patch, LEGACY_ITEM[name][i]):
                index = i
            else:
                break
    
    if index > -1:
        url = header.settings["DATA_FOLDER"] + 'legacy/item/' + name + '_%s.png' % index
    else:
        url = header.settings["DATA_FOLDER"] + 'item/' + name + '.png'

    if os.path.isfile(url):
        return makeimg(url, width, height)
    return get_scaled_resource('item', width, height)

def get_summoner_img(ID, width=0, height=0):
    """gets summoner spell icon
    
    Args:
        ID (int): summoner spell id
        width (int, optional): Scales output. Defaults to 0.
        height (int, optional): Scales output. Defaults to 0.
    
    Returns:
        QPixmap: width x height summoner spell icon
    """
    url = header.settings["DATA_FOLDER"] + 'summoner/' + SUMMONERS[str(ID)] + '.png'
    if os.path.isfile(url):
        return makeimg(url, width, height)

def makeimg(url, width=0, height=0):
    """retrieves image from disk
    
    Args:
        url (str): location of image on disk
        width (int, optional): Scales output. Defaults to 0.
        height (int, optional): Scales output. Defaults to 0.
    
    Returns:
        QPixmap: the image
    """
    pixmap = QPixCache(url)
    if height and width:
        pixmap = pixmap.scaled(width, height, Qt.KeepAspectRatio,
                               Qt.SmoothTransformation)
    return pixmap

class abstractButton():
    clicked = pyqtSignal()

    @abstractmethod
    def __init__(self):
        self.mousein = False

    @abstractmethod
    def onhover(self): pass

    @abstractmethod
    def onleave(self): pass

    @abstractmethod
    def onclick(self): pass

    def mouseMoveEvent(self, event):
        self.mousein = QRectF(self.rect()).contains(event.pos())

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.onclick()

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.LeftButton:
            if self.mousein:
                self.clicked.emit()
                self.onhover()
            else:
                self.onleave()

    def enterEvent(self, event):
        self.mousein = True
        self.onhover()

    def leaveEvent(self, event):
        self.mousein = False
        self.onleave()

class collectionBtn(abstractButton, QWidget):
    """QWidget button modifying styles of QLabels
    
    Args:
        abstractButton ([type]): [description]
        QWidget ([type]): [description]
    """
    def __init__(self):
        super().__init__()
        super(QWidget, self).__init__(PARENTPTR)
        self.qlstrs = []
        self.qlimgs = []
        self.styles = []
        self.setCursor(Qt.PointingHandCursor)

    def append(self, ql, style = ''):
        if len(style) == 0:
            self.qlimgs.append(ql)
        else:
            self.qlstrs.append(ql)
            self.styles.append(style)

    def onleave(self):
        for q in self.qlimgs:
            q.normalize()
        for i in range(len(self.qlstrs)):
            self.qlstrs[i].setStyleSheet(get_style(self.styles[i]))
    
    def onhover(self):
        for q in self.qlimgs:
            q.brighten()
        for i in range(len(self.qlstrs)):
            self.qlstrs[i].setStyleSheet(
                get_style(self.styles[i]+'-hover'))
        
    def onclick(self):
        for q in self.qlimgs:
            q.darken()
        for i in range(len(self.qlstrs)):
            style = get_style(self.styles[i]+'-click')
            if len(style):
                self.qlstrs[i].setStyleSheet(style)

class button(abstractButton, QLabel):
    """Button with hover and click styles. Be sure to call setIco()
    
    emits clicked
    """
    def __init__(self):
        super().__init__()
        super(QLabel, self).__init__(PARENTPTR)
        self.setCursor(Qt.PointingHandCursor)

    def onleave(self):
        self.setPixmap(self.normal)
    
    def onhover(self):
        self.setPixmap(self.hover)

    def onclick(self):
        self.setPixmap(self.click)

    def setIco(self, string, w=0, h=0):
        try:
            self.string = string
            self.normal = get_resource(string)
            self.hover = get_resource(string + '-hover')
            self.click = get_resource(string + '-click')
            #self.disabled = get_resource(string+'-disabled')
            if w:
                if h == 0:
                    h = w
                self.normal = self.normal.scaled(w, h, Qt.KeepAspectRatio,
                                                 Qt.SmoothTransformation)
                if self.hover:
                    self.hover = self.hover.scaled(w, h, Qt.KeepAspectRatio,
                                                   Qt.SmoothTransformation)
                if self.click:
                    self.click = self.click.scaled(w, h, Qt.KeepAspectRatio,
                                                   Qt.SmoothTransformation)
                # self.resize(w,h)
            self.setPixmap(self.normal)
            self.setFixedWidth(w)
            self.setFixedHeight(h)
            # self.setMask(self.pixmap().mask());

        except Exception as ex:
            print(type(ex).__name__, ex.args)

    def setsize(self, w, h=0):
        if h == 0:
            h = w
        self.setIco(self.string, w, h)

class textbutton(abstractButton, QLabel):
    """Creates a text button with hovered and click styles
    
    Args:
        text (str): Text to be displayed on button
        normal (str): Stylesheet
        hover (str, optional): Stylesheet on hover. Defaults to 0.
        click (str, optional): Stylesheet on click. Defaults to 0.
        istab (bool, optional): Whether the button stays (visually) pressed. Defaults to False.
    """
    def __init__(self, text, normal, hover=0, click=0, istab=False):
        try:
            super().__init__()
            super(QLabel, self).__init__(text, PARENTPTR)
            self.mousein = False
            self.normal = normal
            self.hover = hover if hover else normal
            self.click = click if click else self.hover
            self.setStyleSheet(normal)
            self.setCursor(Qt.PointingHandCursor)
            self.down = False
            if istab:
                self.clicked.connect(lambda s=self: s.press())

        except Exception as ex:
            print(type(ex).__name__, ex.args)

    def onleave(self):
        if not self.down:
            self.setStyleSheet(self.normal)
    
    def onhover(self):
        self.setStyleSheet(self.hover)

    def onclick(self):
        if not self.down:
            self.setStyleSheet(self.click)

    def press(self):
        self.down = True
        self.setStyleSheet(self.hover)

    def unpress(self):
        self.down = False
        self.setStyleSheet(self.normal)

class bistateBtn(collectionBtn):
    """button with two sets of icons
    """
    def __init__(self):
        super().__init__()
        self.tqlimg = [], []
        self.state = 0
        self.qlimgs = self.tqlimg[0]
        def change_state(self):
            for b in self.tqlimg[self.state]:
                b.hide()
            self.state = +(not self.state)
            for b in self.tqlimg[self.state]:
                b.show()
        self.clicked.connect(lambda s=self:change_state(s))

    def append(self, ql0, ql1 = None, style = ''):
        if len(style) == 0:
            self.tqlimg[0].append(ql0)
            self.tqlimg[1].append(ql1)
        else:
            self.qlstrs.append(ql0)
            self.styles.append(style)

    def setIco(self, img0, img1, size, text=0, style=0):
        self.lo = QHBoxLayout(self)
        self.lo.setAlignment(Qt.AlignLeft)
        self.lo.setContentsMargins(0,0,0,0)
        ql0 = trimg(get_scaled_resource(img0, size), get_scaled_resource(img0+'-hover', size), get_scaled_resource(img0+'-click', size))
        ql0.setFixedSize(size, size)
        ql1 = trimg(get_scaled_resource(img1, size), get_scaled_resource(img1+'-hover', size), get_scaled_resource(img1+'-click', size))
        ql1.setFixedSize(size, size)
        ql1.hide()
        self.append(ql0, ql1)
        self.lo.addWidget(ql0)
        self.lo.addWidget(ql1)

        if text and style:
            qlstr = QLabel(text)
            qlstr.setStyleSheet(get_style(style))
            self.append(qlstr, style=style)
            self.lo.addWidget(qlstr)


    def off(self):
        if self.state == 1:
            self.state = 0
            for b in self.tqlimg[0]:
                b.show()
            for b in self.tqlimg[1]:
                b.hide()
    
    def on(self):
        if self.state == 0:
            self.state = 1
            for b in self.tqlimg[1]:
                b.show()
            for b in self.tqlimg[0]:
                b.hide()

    def onclick(self):
        super().onclick()

class tab(list):
    """list that keeps track of the active item
    """
    def __init__(self, on, off, active = 0):
        super()
        self.active = active
        self.prev_value = 0
        self.on = on
        self.off = off
    
    def switchto(self, i):
        if len(self) > i and i != self.active:
            if self.active >= 0:
                self.off(self[self.active])
            if i >= 0:
                self.on(self[i])
            self.active = i

class LineEdit(QLineEdit):
    """textbox with custom styling and clear button
    """
    def __init__(self):
        super(QLineEdit, self).__init__(PARENTPTR)
        self.setStyleSheet(get_style('inactive'))

        try:
            self.clearButton = button()
            self.clearButton.setParent(self)
            self.clearButton.setIco('x', 10, 10)
            self.clearButton.setStyleSheet(
                '*{border:none; padding:0px;}')
            self.clearButton.setCursor(Qt.ArrowCursor)
            self.clearButton.clicked.connect(self.clear)
            self.clearButton.hide()
            self.textChanged.connect(self.toggleClearButton)
        except Exception as ex:
            template = "Exception type: {0}\nArguments: {1!r}"
            message = template.format(type(ex).__name__, ex.args)
            print(message)

    def toggleClearButton(self):
        if len(self.text()) > 0:
            self.clearButton.setVisible(True)
        else:
            self.clearButton.hide()

    def resizeEvent(self, event):
        h = self.clearButton.height()
        y = math.ceil((event.size().height() - h) / 2)
        x = event.size().width() - h - y
        # self.clearButton.setsize(h)
        self.clearButton.move(x, y)

    def paintEvent(self, event):
        QLineEdit.paintEvent(self, event)

def sentence_case(string):
    """converts 'UPPER_CASE' to 'Sentence Case'
    
    Args:
        string (str): UPPER_CASE
    
    Returns:
        str: Sentence Case
    """
    string2 = ""
    prevspace = True
    for c in string:
        if c == '_':
            prevspace = True
            string2 += ' '
        elif prevspace:
            string2 += c
            prevspace = False
        else:
            string2 += c.lower()
    return string2

def make_settings_layout(toplayout):
    """creates the settings layout
    """
    WIDTH = 200
    global settings_changed
    settings_changed = 0

    def labeltbox(string, row):
        global settings
        lo_value = QVBoxLayout()
        lo_button = QVBoxLayout()
        layout.addWidget(QLabel(sentence_case(string)), row, 1)

        val = QLabel(header.settings[string])
        val.setTextInteractionFlags(Qt.TextSelectableByMouse)
        val.setCursor(Qt.IBeamCursor)
        val.setFixedHeight(20)
        lo_value.addWidget(val)

        edit = button()
        edit.setIco('edit', 20)
        lo_button.addWidget(edit)

        back = button()
        back.setIco('undo', 20)
        back.hide()
        lo_button.addWidget(back)
        layout.addLayout(lo_button, row, 4)

        tbox = LineEdit()
        tbox.setText(header.settings[string])
        
        tbox.hide()
        lo_value.addWidget(tbox)
        layout.addLayout(lo_value, row, 2)

        tbox.returnPressed.connect(lambda: set_setting(tbox.text(), string))
        tbox.returnPressed.connect(lambda: val.setText(tbox.text()))
        tbox.returnPressed.connect(tbox.hide)
        tbox.returnPressed.connect(edit.show)
        tbox.returnPressed.connect(back.hide)
        tbox.returnPressed.connect(val.show)
        def change_var():
            global settings_changed
            settings_changed = 1
        tbox.returnPressed.connect(change_var)

        edit.clicked.connect(tbox.show)
        edit.clicked.connect(edit.hide)
        edit.clicked.connect(back.show)
        edit.clicked.connect(val.hide)

        back.clicked.connect(tbox.hide)
        back.clicked.connect(edit.show)
        back.clicked.connect(back.hide)
        back.clicked.connect(val.show)
        back.clicked.connect(lambda: tbox.setText(header.settings[string]))
        
    try:
        lovb = QVBoxLayout()
        layout = QGridLayout()
        layout.setColumnStretch(2, 1)

        def leave_settings():
            global settings_changed
            if current_search != 0 and settings_changed == 1:
                settings_changed = 0
                display(current_search)
            pages.switchto(0) if pages.active else pages.switchto(1)

        setico = button()
        setico.setIco("settings", 60 * SCALE)
        setico.clicked.connect(leave_settings)
        lovb.addWidget(setico, 1, Qt.AlignRight)

        fields = ['LOCALE', 'NAME', 'REPLAY_FOLDER', 'FONT_SIZE', 'MATCH_LANGUAGE', 'MATCH_SERVER']
        for i in range(len(fields)):
            labeltbox(fields[i], i)
        lovb.addLayout(layout)

        categories = [
            (_('Visibility'),[_('Champion'), _('Runes'), _('Summoner Spells'), _('Items'),
                _('Position'), _('Win'), _('KDA'), _('KD'), _('KP'), _('CS'), _('CS/m'), _('Gold'),
                _('Gold/m'), _('Multikill'), _('Download Button'), _('Teams'), _('Time')]),
            (_('Connect to Internet'), [_('Connect to LoL client'), _('Auto update images'),
                _('Redownload legacy images')])
            ]
        def update_vis(state):
            p = len(header.settings['VIS'])
            header.settings['VIS']=state[:p]
            header.settings['CLIENT']=bool(state[p])
            header.settings['UPDATE']=bool(state[p+1])
            header.settings['LEGACY']=bool(state[p+2])
        cbt = checkbtn_tree(categories, update_vis)
        lovb.addWidget(cbt.qwbuttons)
        cbt.set_state(header.settings['VIS'] + [header.settings['CLIENT'],
            header.settings['UPDATE'], header.settings['LEGACY']])

        toplayout.addStretch(1)
        toplayout.addLayout(lovb, 2)
        toplayout.addStretch(1)
    except Exception as ex:
        print(type(ex).__name__, ex.args)

def make_main_layout(layout):
    """creates the main menu layout
    """
    top = QHBoxLayout()

    top.addStretch(1)
    searchbar = LineEdit()
    searchbar.returnPressed.connect(lambda: search(searchbar.text()))
    top.addWidget(searchbar, 4)
    setico = button()
    setico.setIco("settings", 60 * SCALE)
    setico.clicked.connect(lambda: pages.switchto(0) if pages.active else pages.switchto(1))

    top.addWidget(setico, 1, Qt.AlignRight)

    warning = button()
    warning.setIco('warning', 30)
    warning.hide()
    WARNING_WIDGET.append(warning)
    warningtxt = QLabel()
    warningtxt.hide()
    WARNING_WIDGET.append(warningtxt)
    if len(warnings) > 0:
        warn('')

    layout.addWidget(warning, 0, Qt.AlignLeft)
    layout.addWidget(warningtxt, 0, Qt.AlignLeft)
    layout.addLayout(top)
    layout.addSpacing(10)
    layout.setSpacing(0)

    block = QHBoxLayout()

    layout.addLayout(block)
    return searchbar

def zoom(i):
    global SCALE
    if i > 0:
        SCALE += 0.1
    elif i < 0 and SCALE != 0.1:
        SCALE -= 0.1
    else:
        SCALE = 0.5
    display(current_search)

def set_main_layout():
    TOP_LAYOUT.removeWidget(pages[0].parentWidget())
    clear_layout(pages[0])
    main = QWidget()
    pages[0] = QVBoxLayout(main)
    make_settings_layout(pages[1])
    bar = make_main_layout(pages[0])
    TOP_LAYOUT.addWidget(main)
    bar.setFocus()

class spinning_img(QWidget):
    """QWidget with an animated rotating image
    
    Args:
        img (QPixmap): image to rotate
        mspr (int): milliseconds per rotation
        clockwise (bool, optional): rotation is clockwise. Defaults to True.
    """
    def __init__(self, img, mspr, clockwise = True):
        super().__init__(PARENTPTR)
        self.img = img
        self.angle = 45
        anim = QVariantAnimation()
        anim.setDuration(mspr)
        anim.setLoopCount(-1)
        self.setSizePolicy(QSizePolicy.MinimumExpanding,
            QSizePolicy.MinimumExpanding)
        if clockwise:
            anim.setStartValue(0)
            anim.setEndValue(360)
        else:
            anim.setStartValue(360)
            anim.setEndValue(0)
        def rotate(self, degree):
            self.angle = degree
            self.update()
        anim.valueChanged.connect(lambda a, s=self: rotate(s,a))
        anim.start(QAbstractAnimation.DeleteWhenStopped)
        self.destroyed.connect(lambda s, a=anim: a.stop())

    def sizeHint(self):
        return self.img.size()

    def minimumSizeHint(self):
        return self.img.size()

    def paintEvent(self, event):
        p = QPainter(self)
        p.setRenderHint(QPainter.SmoothPixmapTransform)
        center = QPointF(self.img.width()/2, self.img.height()/2)
        center2 = QPointF(event.rect().width()/2, event.rect().height()/2)
        # transformations are in reverse order! (-center, rotate, THEN center2)
        p.translate(center2)
        p.rotate(self.angle)
        p.drawPixmap(-center, self.img)
        p.end()

def make_loading_layout(layout):
    qw = spinning_img(get_scaled_resource('loading', 200*SCALE, 200*SCALE), 5000)
    qw.setFixedSize(qw.sizeHint())
    global loadingql
    loadingql = QLabel("Loading...")
    loadingql.setAlignment(Qt.AlignCenter)
    lo = QVBoxLayout()
    lo.addStretch(1) 
    lo.addWidget(qw, Qt.AlignBottom)
    lo.addWidget(loadingql)
    lo.addStretch(1)
    layout.addStretch(1)
    layout.addLayout(lo)
    layout.addStretch(1)

class App(QDialog):
    def __init__(self):
        super().__init__()
        def initialization():
            if 'loadingql' in globals():
                loadingql.setText(_('Indexing replay files'))
            index_replays()
            if header.settings["UPDATE"] and 'loadingql' in globals():
                loadingql.setText(_('Updating images'))
                update()
            if header.settings["LEGACY"]:
                download_legacy()
            if 'loadingql' in globals():
                loadingql.setText(_('Building lists'))
            build_lists()

        self.title = 'Replay Parser'
        self.left = 0
        self.top = 0
        self.width = 810
        self.height = 300
        make_styles()
        self.setStyleSheet(get_style('main'))
        init()
        self.initUI()
        initialization()
        set_main_layout()

    def mousePressEvent(self, event):
        focused_widget = QApplication.focusWidget()
        if isinstance(focused_widget, LineEdit):
            focused_widget.clearFocus()
    
    def keyPressEvent(self, event):
        if event.modifiers() == Qt.ControlModifier:
            if event.key() == Qt.Key_Equal:
                zoom(1)
            if event.key() == Qt.Key_Minus:
                zoom(-1)
            if event.key() == Qt.Key_0:
                zoom(0)
    
    def wheelEvent(self, event):
        if event.modifiers() == Qt.ControlModifier:
            zoom(event.angleDelta().y())

    def initUI(self):
        global pages
        global TOP_LAYOUT
        global PARENTPTR

        pages = tab(lambda s:s.parentWidget().show(), lambda s:s.parentWidget().hide())
        PARENTPTR = self
        self.setWindowTitle(self.title)
        self.setGeometry(self.left, self.top, self.width, self.height)
        self.setWindowFlags(Qt.WindowMinimizeButtonHint
                            | Qt.WindowMaximizeButtonHint
                            | Qt.WindowCloseButtonHint)

        color = qcolors.gray.name()
        rc('axes',edgecolor='#063B45')
        rc('axes.spines', top=False, right = False)
        rc('xtick', color=color, bottom=False)
        rc('ytick', color=color, left=False)
        rc('grid', color=color)
        rc('text', color='white')
        main_widget = QWidget()
        main_layout = QHBoxLayout(main_widget)
        make_loading_layout(main_layout)

        pages.append(main_layout)

        sett_widget = QWidget()
        sett_layout = QHBoxLayout(sett_widget)
        pages.append(sett_layout)
        sett_widget.hide()

        TOP_LAYOUT = QVBoxLayout(self)
        TOP_LAYOUT.addWidget(main_widget)
        TOP_LAYOUT.addWidget(sett_widget)
        self.setLayout(TOP_LAYOUT)
        self.show()

    def closeEvent(self, event):
        save()
