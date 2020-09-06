from dataclasses import dataclass
from termcolor import colored
import colorama
import configparser
import requests
import re

## Necessary for ANSI colors used in termcolor to work with the windows terminal
colorama.init()
#****************************************************************************#
#                               Global Variables   	                         #
#****************************************************************************#

parser = configparser.ConfigParser()
parser.read_file(open('cfg.ini'))
MyUsername = parser['DEFAULT']['Username']
MyPassword = parser['DEFAULT']['Password']
MangaFile = parser['DEFAULT']['MangaFile']

MangaList= list()
HmtlPage = None
MajorSeassion = None
MajorSeassionFlag = 0

Website = {}
Website['OriginKey']='https://mangadex.org/search?author=$$Author$$&tag_mode_exc=any&tag_mode_inc=all&title=$$MangaName$$'
Website['MangaTxKey']='https://mangatx.com/?s=$$MangaName$$&post_type=wp-manga'
Website['WebtoonxyzKey']='https://www.webtoon.xyz/?s=$$MangaName$$&post_type=wp-manga'
Website['MangakakalotKey']='https://mangakakalot.com/search/story/$$MangaName$$'

#Clean Regex '(?<=.)\^\D+(?!\^)\w+\^\w+'

Regex = {}
Regex['OriginKey']= r'(?<=<div><span class=\\\'rounded flag flag-)..(?=\\\' title=\\\'.+\\\'></span></div>)'
#Regex['MangaTxKey']=r'(?!href="https://mangatx\.com/manga/(\S+/chapter-))\d+(?=/\?style=paged">Chapter \d+</a></span>)'
Regex['MangaTxKey']=r'(?<=href="https://mangatx\.com/manga/)\S+/chapter-(\d+|\d+-\d+)(?=/\?style=paged">Chapter \d+|\d+-\d+</a></span>)'
Regex['WebtoonxyzKey']=r'(?!href="https://mangatx\.com/manga/(\S+/chapter-))\d+(?=/\?style=paged">Chapter \d+</a></span>)'
Regex['MangakakalotKey']=r'(?<=<em class="story_chapter">\n)(<a href="https://manga|<a rel="nofollow" href="https://manga)[a-z]+\.com/chapter/\S+/chapter_(\d+|\d+\.\d+|\d+_\d+)(?=" title=")'
#Regex.append('(?<=\<a rel=\"nofollow\" href=\"https:\/\/manganelo\.com\/chapter\/).+?(?=\/chapter_)')
#Regex.append('(?<=\\n<a href=\"https:\/\/mangakakalot\.com\/chapter\/).+?(?=\/chapter_)')

Format = {}
Format['OriginKey']={' ':'%20','\'':'%27',',':'%2C',':':'%3A'}
Format['MangaTxKey']={' ':'+',',':'%2C','!':'%21',':':'%3A'}
Format['WebtoonxyzKey']={' ':'+',',':'%2C','!':'%21','\'':'%27',':':'%3A'}
Format['MangakakalotKey']={' ':'_',',':'_','!':'','\'':'',':':'','.':''}

#****************************************************************************#
#                               Global Variables   	                         #
#****************************************************************************#

@dataclass
class MyMangaStruct(object):
	def __init__(self,Name,Author,ChapterRead,Origin,WebsiteKey,NewChapter):
		self.Name = Name
		self.Author = Author
		self.ChapterRead = ChapterRead
		self.Origin = Origin
		self.WebsiteKey = WebsiteKey
		self.NewChapter = NewChapter

#****************************************************************************#
#                          Functions Implementation                          #
#****************************************************************************#

def PopulateMangaList():
	with open(MangaFile, 'r', encoding='utf8') as mangaFile:
		for manga in mangaFile:
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
			else:
				print(str(n)+' - '+colored('Unable to find '+MangaList[n].Name+' on anywebsite','yellow'))

def GetMangaDexSession():
	global MajorSeassion,MajorSeassionFlag
	url = 'https://mangadex.org/ajax/actions.ajax.php?function=login&amp;nojs=1'
	with requests.session() as session:
		payload = {
					"login_username": MyUsername,
					"login_password": MyPassword
				  }
		
		header = {
					'x-requested-with': 'XMLHttpRequest'
				 }
	if(MyUsername == 'ValidMangaDexUsername'):
		print('Please update the \'cfg.ini\' with a valid Username and Password for MangaDex to continue')
		exit()
	else:
		if(MajorSeassionFlag == 0): 		  
			req = session.post(url,headers=header,data=payload)
			try:
				if(req.status_code == 200):
					MajorSeassionFlag = 1
					MajorSeassion = session
					return session
			except:
				print('Failed at creating a session')
		else:
			return MajorSeassion							

def DisplayDiff(n):
	Diff = 	float(MangaList[n].NewChapter)-float(MangaList[n].ChapterRead)
	if(Diff > 0):
		color='green'
	else:
		color='red'
	if(Diff != 0):
		print(str(n)+' - '+MangaList[n].Name+":"+ colored(str(round(Diff,1)),color))

def GetNewChapters(n):
	if((MangaList[n].Origin == 'None') or (MangaList[n].Origin == 'None\n')):
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
		print(str(n)+' - '+colored("Failed to calculate Diff",'red'))
	
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


def GetMangaOrigin(n):
	session = GetMangaDexSession()
	resp = session.get(GetFormatedUrl(n,'OriginKey'))
	Org = re.search(Regex['OriginKey'],str(resp.content))
	try:
		return Org[0]
	except:
		print(str(n)+' - '+colored('Failed to get '+MangaList[n].Name+' Origin','yellow'))
		return 'None'

def GetFormatedUrl(n,Key:str):
	NameSub = "".join([Format[Key].get(c, c) for c in MangaList[n].Name])
	AuthorSub = "".join([Format[Key].get(c, c) for c in MangaList[n].Author])
	if(Key == 'OriginKey' or Key == 'MangakakalotKey'):
		UrlText = Website[Key].replace("$$MangaName$$",NameSub).replace("$$Author$$",AuthorSub)
	elif(Key == 'MangaTxKey'or Key == 'WebtoonxyzKey'):
		UrlText = Website[Key].replace("$$MangaName$$",NameSub)
	return UrlText

def UpdateMangaFile():
	global MangaList
	i=0
	MyMangaFile = open(MangaFile, 'r', encoding='utf8') 
	MyMangaLines = MyMangaFile.readlines()
	for Line in (MyMangaLines):
		Tmp = str(MangaList[i].Name) + "^" + str(MangaList[i].Author) + "^" + str(MangaList[i].ChapterRead).strip('\n') + "^"  
		Tmp += str(MangaList[i].Origin) + "^" + str(MangaList[i].WebsiteKey) + "^"
		Tmp += (str(MangaList[i].NewChapter)+'\n') if (str(MangaList[i].NewChapter).find('\n') == -1) else (str(MangaList[i].NewChapter))
		MyMangaLines[i] = Tmp
		i += 1
	MyMangaFile = open(MangaFile, 'w', encoding='utf8') 
	MyMangaFile.writelines(MyMangaLines)
	MyMangaFile.close()

def main():
	global MajorSeassion
	PopulateMangaList()
	for i in range (len(MangaList)):
		GetNewChapters(i)
	UpdateMangaFile()

#****************************************************************************#
#                               Main Entry Point   	                         #
#****************************************************************************#
if __name__ == '__main__':
	main()