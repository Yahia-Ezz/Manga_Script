# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'QTPy.ui'
#
# Created by: PyQt5 UI code generator 5.13.2
#
# WARNING! All changes made in this file will be lost!


from PyQt5 import QtCore, QtGui, QtWidgets
import configparser, requests, re, sys
import atexit , math
import os 


#****************************************************************************#
#                               Startup __init__   	                         #
#****************************************************************************#
parser = configparser.ConfigParser()
parser.read_file(open('cfg.ini'))
MyUsername = parser['DEFAULT']['Username']
MyPassword = parser['DEFAULT']['Password']
MangaFile = parser['DEFAULT']['MangaFile']

#****************************************************************************#
#                               Global Variables   	                         #
#****************************************************************************#
MangaList= list()
HmtlPage = None
MajorSeassion = None
MajorSeassionFlag = 0
MajorGUIListIndex = 1

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
#                              User Classes		  	                         #
#****************************************************************************#

class MyMangaStruct(object):
	def __init__(self,Name,Author,ChapterRead,Origin,WebsiteKey,NewChapter):
		self.Name = Name
		self.Author = Author
		self.ChapterRead = ChapterRead
		self.Origin = Origin
		self.WebsiteKey = WebsiteKey
		self.NewChapter = NewChapter

class Ui_mainWindow(object):
	def setupUi(self, mainWindow):
		mainWindow.setObjectName("mainWindow")
		mainWindow.resize(768, 600)
		self.centralwidget = QtWidgets.QWidget(mainWindow)
		self.centralwidget.setObjectName("centralwidget")
		self.NewMangaList = QtWidgets.QListWidget(self.centralwidget)
		self.NewMangaList.setGeometry(QtCore.QRect(20, 10, 341, 411))
		self.NewMangaList.setObjectName("NewMangaList")
		item = QtWidgets.QListWidgetItem()
		font = QtGui.QFont()
		font.setBold(True)
		font.setUnderline(True)
		font.setWeight(75)
		item.setFont(font)
		item.setFlags(QtCore.Qt.NoItemFlags)
		self.NewMangaList.addItem(item)
		#*********************************************************************#
		#                        Image Display label	  	                  #
		#*********************************************************************#
		self.ImageDisplay = QtWidgets.QLabel(self.centralwidget)
		self.ImageDisplay.setGeometry(QtCore.QRect(430, 10, 221, 281))
		self.ImageDisplay.setText("")
		self.ImageDisplay.setScaledContents(True)
		self.ImageDisplay.setObjectName("ImageDisplay")
		#*********************************************************************#
		#                    Fetch NewManga PushButton 	    	              #
		#*********************************************************************#
		self.pushButton = QtWidgets.QPushButton(self.centralwidget)
		self.pushButton.setGeometry(QtCore.QRect(130, 440, 101, 31))
		self.pushButton.setObjectName("pushButton")
		#*********************************************************************#
		#                         	Progress Bar   	  		                  #
		#*********************************************************************#
		self.progressBar = QtWidgets.QProgressBar(self.centralwidget)
		self.progressBar.setGeometry(QtCore.QRect(20, 490, 381, 31))
		self.progressBar.setMaximum(100)
		self.progressBar.setProperty("value", 0)
		self.progressBar.setObjectName("progressBar")
		#*********************************************************************#
		#                       Description label  			                  #
		#*********************************************************************#
		self.label = QtWidgets.QLabel(self.centralwidget)
		self.label.setGeometry(QtCore.QRect(400, 310, 351, 241))
		self.label.setTextInteractionFlags(QtCore.Qt.TextBrowserInteraction)
		self.label.setObjectName("label")
		mainWindow.setCentralWidget(self.centralwidget)
		self.menubar = QtWidgets.QMenuBar(mainWindow)
		self.menubar.setGeometry(QtCore.QRect(0, 0, 768, 21))
		self.menubar.setObjectName("menubar")
		mainWindow.setMenuBar(self.menubar)
		self.statusbar = QtWidgets.QStatusBar(mainWindow)
		self.statusbar.setObjectName("statusbar")
		mainWindow.setStatusBar(self.statusbar)
		self.retranslateUi(mainWindow)
		self.NewMangaList.currentItemChanged['QListWidgetItem*','QListWidgetItem*'].connect(self.ItemChanged)
		QtCore.QMetaObject.connectSlotsByName(mainWindow)

	def retranslateUi(self, mainWindow):
		_translate = QtCore.QCoreApplication.translate
		mainWindow.setWindowTitle(_translate("mainWindow", "Manga Fetcher Script"))
		item = self.NewMangaList.item(0)
		item.setText(_translate("mainWindow", "Read   |                 Manga Name                                                      "))
		self.pushButton.setText(_translate("mainWindow", "Fetch New Manga"))
		self.label.setText(_translate("mainWindow", "Please press the fetch new manga button to start"))
		self.pushButton.clicked.connect(self.FetchNewMangaButton)

	def ClearList(self):
		global MajorGUIListIndex
		MajorGUIListIndex =1
		self.NewMangaList.clear()

	def FetchNewMangaButton(self):
		for i in range (len(MangaList)):
			GetNewChapters(i)
			GetMangaImages(i)
			self.progressBar.setProperty("value",(math.ceil((i*100)/(len(MangaList)-1))))

	def ItemChanged(self):
		self.ImageDisplay.setPixmap(QtGui.QPixmap(os.getcwd()+"\\cache\\"+(str(self.NewMangaList.currentItem().text()).replace('?',"").replace(':',""))+".jpg"))
		self.label.setFont(QtGui.QFont("Times",pointSize =12,weight=QtGui.QFont.Bold))
		self.label.setOpenExternalLinks(True)
		n = int(self.NewMangaList.currentItem().whatsThis())
		self.label.setText("Last Read Chapter : "+MangaList[n].ChapterRead+"\n\n\
Latest Chapter : "+MangaList[n].NewChapter+"\n\n\
Link : \n"+GetFormatedUrl(n,'MangaTxKey' if(MangaList[n].Origin == 'cn') else ('MangakakalotKey' if(MangaList[n].Origin == 'jp' ) else 'WebtoonxyzKey') ))

#****************************************************************************#
#                          Functions Implementation                          #
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

			MangaList.append(MyMangaStruct(Name,Author,ChapterRead,Origin,WebsiteKey,NewChapter))

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
		Tmp += (str(MangaList[LineIx].NewChapter)+'\n') if (str(MangaList[LineIx].NewChapter).find('\n') == -1) else (str(MangaList[LineIx].NewChapter))
		MyMangaLines[LineIx] = Tmp
	MyMangaFile = open(MangaFile, 'w', encoding='utf8') 
	MyMangaFile.writelines(MyMangaLines)
	MyMangaFile.close()

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

def DisplayDiff(n):
	global MajorGUIListIndex
	Diff = 	float(MangaList[n].NewChapter)-float(MangaList[n].ChapterRead)
	Diff =  round(Diff,(1 if Diff>0 else 0))
	if(Diff > 0):
		item = QtWidgets.QListWidgetItem()
		item.setFlags(QtCore.Qt.ItemIsSelectable|QtCore.Qt.ItemIsUserCheckable|QtCore.Qt.ItemIsEnabled)
		item.setCheckState(QtCore.Qt.Unchecked)
		item.setWhatsThis(str(n))
		ui.NewMangaList.addItem(item)
		ui.NewMangaList.item(MajorGUIListIndex).setText(MangaList[n].Name)
		MajorGUIListIndex+=1
		
def GetNewChapters(n):
	if(not os.path.exists('cache')):
		os.mkdir((os.getcwd()+"\cache"))	
	if((MangaList[n].Origin == 'None')):
		MangaList[n].Origin=GetMangaOrigin(n)
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
		except:	return
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
	for i in range (1,ui.NewMangaList.count()):
		State = ui.NewMangaList.item(i).checkState()
		n = int(ui.NewMangaList.item(i).whatsThis())
		if( State == 2 ):
			MangaList[n].ChapterRead = MangaList[n].NewChapter
				
#****************************************************************************#
#                               Main Entry Point   	                         #
#****************************************************************************#
if __name__ == "__main__":
	atexit.register(exit_handler)
	PopulateMangaList()
	app = QtWidgets.QApplication(sys.argv)
	mainWindow = QtWidgets.QMainWindow()
	ui = Ui_mainWindow()
	ui.setupUi(mainWindow)
	mainWindow.show()
	sys.exit(app.exec_())










