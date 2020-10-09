 ############################################################################################
 #               __  __                            _____          _        _                # 
 #              |  \/  |                          / ____|        (_)      | |               #
 #              | \  / | __ _ _ __   __ _  __ _  | (___   ___ _ __ _ _ __ | |_              #
 #              | |\/| |/ _` | '_ \ / _` |/ _` |  \___ \ / __| '__| | '_ \| __|             #
 #              | |  | | (_| | | | | (_| | (_| |  ____) | (__| |  | | |_) | |_              #
 #              |_|  |_|\__,_|_| |_|\__, |\__,_| |_____/ \___|_|  |_| .__/ \__|             #
 #                                   __/ |                          | |                     #                
 #                                  |___/                           |_|                     #
 ############################################################################################

from PyQt5 import QtCore, QtGui, QtWidgets
import configparser, requests, re, sys, os, numpy, PIL
from PIL import Image
import atexit , math

#****************************************************************************#
#                              Startup __init__                              #
#****************************************************************************#
parser = configparser.ConfigParser()
parser.read_file(open('cfg.ini'))
MyUsername = parser['DEFAULT']['Username']
MyPassword = parser['DEFAULT']['Password']
MangaFile = parser['DEFAULT']['MangaFile']

#****************************************************************************#
#                              Global Variables                              #
#****************************************************************************#
MangaList= list()
HmtlPage = None
MajorSeassion = None
MajorSeassionFlag = 0
MajorGUIListIndex = 0
NewImageIndex = -1 
LastImageIndex = -2

Website = {}
Website['OriginKey']='https://mangadex.org/search?author=$$Author$$&tag_mode_exc=any&tag_mode_inc=all&title=$$MangaName$$'
Website['MangaTxKey']='https://mangatx.com/?s=$$MangaName$$&post_type=wp-manga'
Website['WebtoonxyzKey']='https://www.webtoon.xyz/?s=$$MangaName$$&post_type=wp-manga'
Website['MangakakalotKey']='https://mangakakalot.com/search/story/$$MangaName$$'

Regex = {}
Regex['OriginKey']= r'(?<=<div><span class=\\\'rounded flag flag-)..(?=\\\' title=\\\'.+\\\'></span></div>)'
Regex['MangaTxKey']=r'(?<=href="https://mangatx\.com/manga/)\S+/chapter-(\d+|\d+-\d+)(?=/\?style=paged">Chapter \d+|\d+-\d+</a></span>)'
Regex['WebtoonxyzKey']=r'(?!href="https://mangatx\.com/manga/(\S+/chapter-))\d+(?=/\?style=paged">Chapter \d+</a></span>)'
Regex['MangakakalotKey']=r'(?<=<em class="story_chapter">\n)(<a href="https://manga|<a rel="nofollow" href="https://manga)[a-z]+\.com/chapter/\S+/chapter_(\d+|\d+\.\d+|\d+_\d+)(?=" title=")'
Regex['ImageKey']=r'(?<=src=")/images/manga/.+?(?=\")'

Format = {}
Format['OriginKey']={' ':'%20','\'':'%27',',':'%2C',':':'%3A'}
Format['MangaTxKey']={' ':'+',',':'%2C','!':'%21',':':'%3A'}
Format['WebtoonxyzKey']={' ':'+',',':'%2C','!':'%21','\'':'%27',':':'%3A'}
Format['MangakakalotKey']={' ':'_',',':'_','!':'','\'':'',':':'','.':''}
#****************************************************************************#
#                             User Classes                                   #
#****************************************************************************#
class MyMangaStruct(object):
    def __init__(self,Name,Author,ChapterRead,Origin,WebsiteKey,NewChapter,Rank):
        self.Name = Name
        self.Author = Author
        self.ChapterRead = ChapterRead
        self.Origin = Origin
        self.WebsiteKey = WebsiteKey
        self.NewChapter = NewChapter
        self.Rank = Rank

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(1018, 600)
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.gridLayout_2 = QtWidgets.QGridLayout(self.centralwidget)
        self.gridLayout_2.setObjectName("gridLayout_2")
        self.gridLayout = QtWidgets.QGridLayout()
        self.gridLayout.setSpacing(10)
        self.gridLayout.setObjectName("gridLayout")
        #****************************************************************************#
        #                             QTableWidget                                   #
        #****************************************************************************#       
        self.tableWidget = QtWidgets.QTableWidget(self.centralwidget)
        self.tableWidget.setObjectName("tableWidget")
        self.tableWidget.setColumnCount(4)
        self.tableWidget.setRowCount(0)
        for i in range(4):
            item = QtWidgets.QTableWidgetItem()
            item.setTextAlignment(QtCore.Qt.AlignCenter)
            font = QtGui.QFont()
            font.setBold(True)
            font.setWeight(75)
            item.setFont(font)
            self.tableWidget.setHorizontalHeaderItem(i, item)
        self.gridLayout.addWidget(self.tableWidget, 0, 0, 5, 3)
        #****************************************************************************#
        #                             QProgressBar                                   #
        #****************************************************************************#        
        self.progressBar = QtWidgets.QProgressBar(self.centralwidget)
        self.progressBar.setProperty("value", 0)
        self.progressBar.setObjectName("progressBar")
        self.gridLayout.addWidget(self.progressBar, 6, 0, 1, 3)
        #****************************************************************************#
        #                             QLabel MangaInfo                               #
        #****************************************************************************#            
        self.MangaInfoLabel = QtWidgets.QLabel(self.centralwidget)
        self.MangaInfoLabel.setObjectName("MangaInfoLabel")
        self.MangaInfoLabel.setTextInteractionFlags(QtCore.Qt.TextBrowserInteraction)
        self.MangaInfoLabel.setOpenExternalLinks(True)
        self.MangaInfoLabel.setWordWrap(True)
        self.gridLayout.addWidget(self.MangaInfoLabel, 2, 3, 5, 2)
        #****************************************************************************#
        #                             QComboBox                                      #
        #****************************************************************************#  
        self.comboBox = QtWidgets.QComboBox(self.centralwidget)
        self.comboBox.setObjectName("comboBox")
        self.comboBox.addItem("All Ranks")
        self.comboBox.addItem("S Rank Only")      
        self.comboBox.addItem("A Rank Only")
        self.comboBox.addItem("B Rank Only")
        self.comboBox.addItem("N Rank Only")
        # self.comboBox.activated.connect(self.FetchRankHandler)
        self.gridLayout.addWidget(self.comboBox, 5, 2, 1, 1)
        #****************************************************************************#
        #                             QLabel Image                                   #
        #****************************************************************************#          
        self.ImageLabel = QtWidgets.QLabel(self.centralwidget)
        self.ImageLabel.setObjectName("ImageLabel")
        self.ImageLabel.setText("")
        self.ImageLabel.setScaledContents(True)
        self.gridLayout.addWidget(self.ImageLabel, 0, 3, 2, 1)
        #****************************************************************************#
        #                             QPushButton                                    #
        #****************************************************************************#             
        self.pushButton = QtWidgets.QPushButton(self.centralwidget)
        self.pushButton.setObjectName("pushButton")
        self.pushButton.clicked.connect(self.FetchManga)
        self.gridLayout.addWidget(self.pushButton, 5, 0, 1, 2)
        #****************************************************************************#
        #                             QSpacers                                       #
        #****************************************************************************#       
        spacerItem = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Minimum)
        self.gridLayout.addItem(spacerItem, 1, 4, 1, 1)
        spacerItem1 = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Minimum)
        self.gridLayout.addItem(spacerItem1, 0, 4, 1, 1)
        self.gridLayout_2.addLayout(self.gridLayout, 0, 0, 1, 1)
        MainWindow.setCentralWidget(self.centralwidget)
        #****************************************************************************#
        #                             QMenuBar                                       #
        #****************************************************************************#        
        self.menubar = QtWidgets.QMenuBar(MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 1018, 21))
        self.menubar.setObjectName("menubar")
        self.menuFile = QtWidgets.QMenu(self.menubar)
        self.menuFile.setObjectName("menuFile")
        MainWindow.setMenuBar(self.menubar)
        #****************************************************************************#
        #                             QStatusBar                                     #
        #****************************************************************************#  
        self.statusbar = QtWidgets.QStatusBar(MainWindow)
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)


        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        TempList = ["Read\nStatus", "Manga\nRank", "Search\nWebsite","Manga Title"]
        TempLayout = ['ResizeToContents', 'ResizeToContents', 'ResizeToContents','Stretch']
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "MainWindow"))
        for i in range(4):
            item = self.tableWidget.horizontalHeaderItem(i)
            item.setText(_translate("MainWindow",TempList[i]))
            self.tableWidget.horizontalHeader().setSectionResizeMode(i,QtWidgets.QHeaderView.Stretch if(TempLayout[i] == 'Stretch') else(QtWidgets.QHeaderView.ResizeToContents))
        self.MangaInfoLabel.setText(_translate("MainWindow", "Press the Fetch Manga pushButton to startc"))
        self.ImageLabel.setText(_translate("MainWindow", ""))
        self.pushButton.setText(_translate("MainWindow", "Fetch Manga"))

    def ChangedCellHandler(self):
        ObjectIndex = int(self.tableWidget.cellWidget(self.tableWidget.currentRow(),self.tableWidget.currentColumn()).objectName())
        ComboText = self.tableWidget.cellWidget(self.tableWidget.currentRow(),self.tableWidget.currentColumn()).currentText()
        if (self.tableWidget.currentColumn() == 1):
            MangaList[ObjectIndex].Rank = ComboText
        else:
            MangaList[ObjectIndex].Origin = 'cn' if (ComboText == 'MangaTx') else 'jp' if(ComboText == 'MangaKakalot') else 'kr'

    def FetchManga(self):
        global MajorGUIListIndex
        if (MajorGUIListIndex != 0):
            MarkChaptersAsRead()
            for i in range (MajorGUIListIndex):
                self.tableWidget.removeRow(i)
            self.tableWidget.setRowCount(0)
            self.tableWidget.update() 
            MajorGUIListIndex = 0
            NewImageIndex = -1 
            LastImageIndex = -2
        for i in range (len(MangaList)):
            FetchNewRanks(i)
            GetMangaImages(i)
            self.progressBar.setProperty("value",(math.ceil((i*100)/(len(MangaList)-1))))
            self.progressBar.repaint()

#****************************************************************************#
#                         Functions Implementation                           #
#****************************************************************************#
def PopulateMangaList():
    with open(MangaFile, 'r', encoding='utf8') as mangaFile:
        for mangaIx,manga in enumerate(mangaFile): 
            manga=[text.strip() for text in manga.split('^')]
            Name=manga[0]
            try: Author=manga[1]
            except: Author='None'
            try: ChapterRead=manga[2]
            except: ChapterRead= '0'
            try: Origin=manga[3]
            except: Origin= 'None'
            try: WebsiteKey=manga[4]
            except: WebsiteKey= 'None'
            try: NewChapter=manga[5]
            except: NewChapter= 'None'
            try: Rank = manga[6] if (manga[6] != 'None') else 'N'
            except:Rank = 'N'
            MangaList.append(MyMangaStruct(Name,Author,ChapterRead,Origin,WebsiteKey,NewChapter,Rank))

def InvalidChapterHandler(n):
    Key = 'MangaTxKey'
    resp = requests.get(GetFormatedUrl(n,Key))
    Chap = re.search(Regex[Key],str(resp.text))
    if(Chap != None):
        MangaList[n].Origin='cn'
        return Chap[1].replace('-','.') 
    else:
        Key = 'MangakakalotKey'
        resp = requests.get(GetFormatedUrl(n,Key))
        Chap = re.search(Regex[Key],str(resp.text))
        if(Chap != None):
            MangaList[n].Origin='jp'
            return Chap[2].replace('-','.')
        else:
            Key = 'WebtoonxyzKey'
            resp = requests.get(GetFormatedUrl(n,Key))
            Chap = re.search(Regex[Key],str(resp.text))
            if(Chap != None):
                MangaList[n].Origin='kr'
                return Chap[0].replace('-','.')

# URL = r'https://www.webtoon.xyz/read/solo-leveling/'
regex = r'(?<=<a href=\"$$URL$$chapter-)\d+(?=/\">\\nChapter \d+ </a>)'

def ImageVerticalConcatination(ImgListNumber:int(),ChapterNumber:int()):
    Imgs=[] ; ImgSize=[] ; CombinedImgs=[]; SumWidth = float()
    for i in range(ImgListNumber):
# Open all the Downloaded images using Pything Image Library in a list.
        Imgs.append(PIL.Image.open("Images\\Ch "+str(ChapterNumber)+"\\"+str(i)+".jpg"))
        SumWidth += int(Imgs[i].size[0])
    AvgWidth = (SumWidth / ImgListNumber )
    for OrigImg in Imgs[::1]:
# Resize all images to match the avg width while maintaining ratio and convert its type to RGB for the stacking to work. 
        NewImg = OrigImg.resize((round(AvgWidth,0),round((OrigImg.size[1]*AvgWidth/OrigImg.size[0]),0)), Image.ANTIALIAS)
        NewImg = NewImg.convert('RGB')
# Transform the images into a matrix.       
        CombinedImgs.append(numpy.asarray(NewImg))

def getUrlChapterLinksDownload(URL):
    resp = requests.get(URL)
    Regex = regex.replace(r'$$URL$$',URL.replace('.','\.'))
    List = re.findall(Regex,str(resp.content))  
    ListChapter = list()
    for i in range(len(List)):
        ListChapter.append(URL+'chapter-'+List[i]+'/')
    ListChapter.reverse()
    for n in range(len(ListChapter)):
        resp = requests.get(str(ListChapter[n]))
        Imgs = re.findall(r'(?<=src=\"\\t\\t\\t\\n\\t\\t\\t)https://cdn1\.webtoon\.xyz/.+?/chapter-\d+/\d+\.jpg(?=\" )',str(resp.content))
        try:os.makedirs('Images\\Ch '+str(n+1))
        except:None
        for i in range(len(Imgs)):
            resp = requests.get(Imgs[i])
            file = open("Images\\Ch "+str(n+1)+"\\"+str(i)+".jpg", "wb")
            file.write(resp.content)
            file.close()
        ImageVerticalConcatination(len(Imgs),n+1)





# Stack images vertically.
    CombinedImgsNewV = numpy.vstack(CombinedImgs)
    CombinedImgsNewV = PIL.Image.fromarray(CombinedImgsNewV)
# Save stack vertically.    
    CombinedImgsNewV.save("Images\\Ch "+str(ChapterNumber)+"\\"+"00-Vertical.png")


def GetMangaDexSession():
    global MajorSeassion,MajorSeassionFlag
    url = 'https://mangadex.org/ajax/actions.ajax.php?function=login&amp;nojs=1'
    session= requests.session()
    payload = {"login_username": MyUsername,"login_password": MyPassword }
    header  = {'x-requested-with': 'XMLHttpRequest' }
    if(MyUsername == 'ValidMangaDexUsername'):
        exit()
    else:
        if(MajorSeassionFlag == 0):           
            req = session.post(url,headers=header,data=payload)
            try:
                if(req.status_code == 200):
                    MajorSeassionFlag = 1
                    MajorSeassion = session
                    return session
            except:None
        else:
            return MajorSeassion                            

def ImageHandler():
    global NewImageIndex, LastImageIndex 
    if( ui.tableWidget.currentColumn() == 3):
        NewImageIndex = ui.tableWidget.currentRow()
        if(NewImageIndex != LastImageIndex):
            n = int(ui.tableWidget.cellWidget(NewImageIndex,2).objectName())
            Link =  GetFormatedUrl(n,'MangaTxKey' if(MangaList[n].Origin == 'cn') else ('MangakakalotKey' if(MangaList[n].Origin == 'jp' ) else 'WebtoonxyzKey') )      
            Description = "Last Read Chapter : "+MangaList[n].ChapterRead+"<br><br>Latest Chapter : "+MangaList[n].NewChapter+"<br><br>Link : "
            Link='<a href="'+str(Link)+'">Manga Link</a><br>'
            ui.ImageLabel.setPixmap(QtGui.QPixmap(os.getcwd()+"\\cache\\"+(ui.tableWidget.item(NewImageIndex,3).text().replace('?',"").replace(':',""))+".jpg"))
            LastImageIndex = NewImageIndex
            ui.MangaInfoLabel.setFont(QtGui.QFont("Times",pointSize =14,weight=QtGui.QFont.Bold))
            ui.MangaInfoLabel.setText(Description+Link)
            ui.ImageLabel.repaint()

def DisplayDiff(n):
    global MajorGUIListIndex
    Diff =  float(MangaList[n].NewChapter)-float(MangaList[n].ChapterRead)
    Diff =  round(Diff,(1 if Diff>0 else 0))
    if(Diff > 0):
        ui.tableWidget.insertRow(ui.tableWidget.rowCount())
        ###################### Read Status ########################
        ui.checkBox = QtWidgets.QCheckBox(MainWindow)
        ui.checkBox.setGeometry(QtCore.QRect(130, 540, 70, 17))
        ui.checkBox.setObjectName(str(n))
        ui.checkBox.setStyleSheet("margin-left:20%; margin-right:15%;")
        ui.tableWidget.setCellWidget(MajorGUIListIndex, 0, ui.checkBox)
        ###################### Manga Rank  ########################
        ui.comboBox1 = QtWidgets.QComboBox(ui.centralwidget)
        ui.comboBox1.setObjectName(str(n))
        ui.comboBox1.addItem("S")
        ui.comboBox1.addItem("A")
        ui.comboBox1.addItem("B")
        ui.comboBox1.addItem("N")
        ui.gridLayout.addWidget(ui.comboBox1, 5, 2, 1, 1)
        ui.tableWidget.setCellWidget(MajorGUIListIndex, 1, ui.comboBox1)
        Index = (0 if(MangaList[n].Rank == 'S') else (1 if(MangaList[n].Rank == 'A')else 2 if(MangaList[n].Rank == 'B')else 3))
        ui.comboBox1.setCurrentIndex(Index)
        ui.comboBox1.activated.connect(ui.ChangedCellHandler)
        #################### Search Website #######################
        ui.comboBox2 = QtWidgets.QComboBox(ui.centralwidget)
        ui.comboBox2.setObjectName(str(n))
        ui.comboBox2.addItem("MangaTx")
        ui.comboBox2.addItem("WebToonXYZ")
        ui.comboBox2.addItem("MangaKakalot")
        ui.gridLayout.addWidget(ui.comboBox2, 5, 2, 1, 1)
        ui.tableWidget.setCellWidget(MajorGUIListIndex, 2, ui.comboBox2)
        Index = (0 if(MangaList[n].Origin == 'cn') else (2 if(MangaList[n].Origin == 'jp')else 1))
        ui.comboBox2.setCurrentIndex(Index)
        ui.comboBox2.activated.connect(ui.ChangedCellHandler)
        ###################### Manga Title ########################
        item = QtWidgets.QTableWidgetItem() 
        ui.tableWidget.setItem(MajorGUIListIndex, 3,item)
        item.setText(QtCore.QCoreApplication.translate("MainWindow", MangaList[n].Name))
        item.setFlags(QtCore.Qt.ItemIsSelectable|QtCore.Qt.ItemIsEnabled)
        ui.tableWidget.itemSelectionChanged.connect(ImageHandler) 
        MajorGUIListIndex+=1
        ###################### Enable Table Signals ########################
        # self.tableWidget.cellClicked['int','int'].connect(ui.oprr)       

def FetchNewRanks(n):
    if(ui.comboBox.currentText().strip(' Rank Only') == 'All Ranks' ):
        GetNewChapters(n)
    elif(ui.comboBox.currentText().strip(' Rank Only') == MangaList[n].Rank):
        GetNewChapters(n)
    else:None

def GetNewChapters(n):
    if(not os.path.exists('cache')):
        os.mkdir((os.getcwd()+"\cache"))    
    if((MangaList[n].Origin == 'None')):
        MangaList[n].Origin= GetMangaOrigin(n)
    if(MangaList[n].Origin == 'cn'):
        MangaList[n].NewChapter = GetLatestChapter(n,'MangaTxKey')
    elif(MangaList[n].Origin == 'kr' or MangaList[n].Origin == 'gb' ):
        MangaList[n].NewChapter = GetLatestChapter(n,'WebtoonxyzKey')
    else:
        MangaList[n].NewChapter = GetLatestChapter(n,'MangakakalotKey')
    try:
        DisplayDiff(n)
    except:
        None
    
def GetLatestChapter(n,Key:str):
    resp = requests.get(GetFormatedUrl(n,Key))
    Chap = re.search(Regex[Key],str(resp.text))
    if(Chap != None ):
        if (Key == 'MangaTxKey'):
            return Chap[1].replace('-','.')
        elif(Key == 'WebtoonxyzKey'):
            return Chap[0].replace('-','.')
        elif(Key == 'MangakakalotKey'):
            return Chap[2].replace('-','.')
    else:
        InvalidChapterHandler(n)

def GetMangaImages(n):
    if(not os.path.isfile(os.getcwd()+"\\cache\\"+(str(MangaList[n].Name).replace('?',"").replace(':',""))+".jpg")):
        if(not MajorSeassionFlag ):
            sessoion = GetMangaDexSession()
        else:
            sessoion = MajorSeassion
        resp = sessoion.get(GetFormatedUrl(n,'OriginKey'))
        ImgLink = re.search(Regex['ImageKey'],str(resp.content))
        try:Link = ImgLink[0]
        except: return
        URL ="https://mangadex.org/"+str(Link)
        resp = sessoion.get(URL)
        file = open("cache\\"+(str(MangaList[n].Name).replace('?',"").replace(':',""))+".jpg", "wb")
        file.write(resp.content)
        file.close()

def GetMangaOrigin(n):
    session = GetMangaDexSession()
    resp = session.get(GetFormatedUrl(n,'OriginKey'))
    Org = re.search(Regex['OriginKey'],str(resp.content))
    try:
        return Org[0]
    except:
        return 'None'

def GetFormatedUrl(n,Key:str):
    NameSub = "".join([Format[Key].get(c, c) for c in MangaList[n].Name])
    AuthorSub = "".join([Format[Key].get(c, c) for c in MangaList[n].Author])
    if(Key == 'OriginKey' or Key == 'MangakakalotKey'):
        UrlText = Website[Key].replace("$$MangaName$$",NameSub).replace("$$Author$$",AuthorSub)
    elif(Key == 'MangaTxKey'or Key == 'WebtoonxyzKey'):
        UrlText = Website[Key].replace("$$MangaName$$",NameSub)
    return UrlText

def MarkChaptersAsRead():
    for i in range (MajorGUIListIndex):
      State = ui.tableWidget.cellWidget(i,0).checkState()
      n = int(ui.tableWidget.cellWidget(i,0).objectName())
      if( State == 2 ):
        MangaList[n].ChapterRead = MangaList[n].NewChapter
    
def exit_handler():
    MarkChaptersAsRead()
    UpdateMangaFile()

def UpdateMangaFile():
    global MangaList
    MyMangaFile = open(MangaFile, 'r', encoding='utf8') 
    MyMangaLines = MyMangaFile.readlines()
    for LineIx,Line in enumerate(MyMangaLines):
        Tmp = str(MangaList[LineIx].Name) + "^" + str(MangaList[LineIx].Author) + "^" + str(MangaList[LineIx].ChapterRead).strip('\n') + "^"  
        Tmp += str(MangaList[LineIx].Origin) + "^" + str(MangaList[LineIx].WebsiteKey) + "^"
        Tmp += (str(MangaList[LineIx].NewChapter)) if (str(MangaList[LineIx].NewChapter) == -1) else (str(MangaList[LineIx].NewChapter))
        Tmp += '^' + str(MangaList[LineIx].Rank)+'\n'
        MyMangaLines[LineIx] = Tmp
    MyMangaFile = open(MangaFile, 'w', encoding='utf8') 
    MyMangaFile.writelines(MyMangaLines)
    MyMangaFile.close()

if __name__ == "__main__":
    atexit.register(exit_handler)
    PopulateMangaList()
    app = QtWidgets.QApplication(sys.argv)
    MainWindow = QtWidgets.QMainWindow()
    ui = Ui_MainWindow()
    ui.setupUi(MainWindow)
    MainWindow.show()
    sys.exit(app.exec_())
