from termcolor import colored
import colorama, configparser, requests, re, sys
from argparse import ArgumentParser
#****************************************************************************#
#                               Startup __init__   	                         #
#****************************************************************************#
parser = configparser.ConfigParser()
parser.read_file(open('cfg.ini'))
MyUsername = parser['DEFAULT']['Username']
MyPassword = parser['DEFAULT']['Password']
MangaFile = parser['DEFAULT']['MangaFile']
## Necessary for ANSI colors used in termcolor to work with the windows terminal
colorama.init()
################################################################################
## Define & Get Arguments
################################################################################
commands = ArgumentParser(description='Manga Script Arguments...')
commands.add_argument('-v', '--verbose',       dest='verbose',       default=10,      type=int,             help='Set verbosity level of program from 0 (off) to 10 (verbal diarrhea).')
commands.add_argument('-m', '--max',           dest='maxManga',      default=1000000, type=int,             help='Max number of mangas to load')
commands.add_argument(      '--printNoUnread', dest='printNoUnread', default=False,   action='store_true',  help='Print no unread chapters')
commands, unknown = commands.parse_known_args()

if(commands.verbose>=10):print('Command to replicate this script: '+colored(' '.join(sys.argv),'white','on_blue'))
if(commands.maxManga!=1000000): print(colored('Max number of mangas to load: '+ str(commands.maxManga),'white','on_magenta')+'\n')
else: print(colored('No max number of mangas to load specified','white','on_magenta')+'\n')

#****************************************************************************#
#                               Global Variables   	                         #
#****************************************************************************#
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
Regex['MangaTxKey']=r'(?<=href="https://mangatx\.com/manga/)\S+/chapter-(\d+|\d+-\d+)(?=/\?style=paged">Chapter \d+|\d+-\d+</a></span>)'
Regex['WebtoonxyzKey']=r'(?!href="https://mangatx\.com/manga/(\S+/chapter-))\d+(?=/\?style=paged">Chapter \d+</a></span>)'
Regex['MangakakalotKey']=r'(?<=<em class="story_chapter">\n)(<a href="https://manga|<a rel="nofollow" href="https://manga)[a-z]+\.com/chapter/\S+/chapter_(\d+|\d+\.\d+|\d+_\d+)(?=" title=")'
#Regex['MangaTxKey']=r'(?!href="https://mangatx\.com/manga/(\S+/chapter-))\d+(?=/\?style=paged">Chapter \d+</a></span>)'
#Regex.append('(?<=\<a rel=\"nofollow\" href=\"https:\/\/manganelo\.com\/chapter\/).+?(?=\/chapter_)')
#Regex.append('(?<=\\n<a href=\"https:\/\/mangakakalot\.com\/chapter\/).+?(?=\/chapter_)')

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

#****************************************************************************#
#                          Functions Implementation                          #
#****************************************************************************#

def PopulateMangaList():

	with open(MangaFile, 'r', encoding='utf8') as mangaFile:
		for mangaIx,manga in enumerate(mangaFile): 
			if mangaIx>=commands.maxManga: continue
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
	session= requests.session()
	payload = {"login_username": MyUsername,"login_password": MyPassword }
	header  = {'x-requested-with': 'XMLHttpRequest' }
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
	Diff =  round(Diff,(1 if Diff>0 else None))
	if(Diff > 0):   color='green'
	elif(Diff==0):  color='cyan'
	else:           color='red'
	if(commands.verbose>=2):
		if(Diff != 0): print(str(n)+' - '+MangaList[n].Name+": "+ colored(str(Diff)+' unread chapter'+('s' if Diff>1 else ''),color))
		elif (commands.printNoUnread): print(str(n)+' - '+MangaList[n].Name+": "+ colored('no unread chapters',color))

def GetNewChapters(n):
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
	MyMangaFile = open(MangaFile, 'r', encoding='utf8') 
	MyMangaLines = MyMangaFile.readlines()
	for LineIx,Line in enumerate(MyMangaLines):
		if LineIx>=commands.maxManga: continue
		Tmp = str(MangaList[LineIx].Name) + "^" + str(MangaList[LineIx].Author) + "^" + str(MangaList[LineIx].ChapterRead).strip('\n') + "^"  
		Tmp += str(MangaList[LineIx].Origin) + "^" + str(MangaList[LineIx].WebsiteKey) + "^"
		Tmp += (str(MangaList[LineIx].NewChapter)+'\n') if (str(MangaList[LineIx].NewChapter).find('\n') == -1) else (str(MangaList[LineIx].NewChapter))
		MyMangaLines[LineIx] = Tmp
	MyMangaFile = open(MangaFile, 'w', encoding='utf8') 
	MyMangaFile.writelines(MyMangaLines)
	MyMangaFile.close()

def DisplayNewChapters():
	print(colored('Fetching New Chapters:','white','on_green'))
	for i in range (len(MangaList)):
		GetNewChapters(i)
	UpdateMangaFile()

def MarkChaptersAsRead():
	print('Please enter the indexes of the chapters to be marked as read :\'0 15 129 ... etc \' and (X) to exit: ')
	Var = input()
	Var = Var.split(' ')
	for i in  range(len(Var)):
		try:
			if( (Var[i].isdigit() == True) and (0 <= int(Var[i]) <= len(MangaList)) ):
				MangaList[int(Var[i])].ChapterRead = MangaList[int(Var[i])].NewChapter
		except:
			None
	UpdateMangaFile()
	print('Done Marking')

def main():
	print('\nPlease choose an Option :\n1 - Fetch new manga chapters\n2 - Mark chapters as read\n3 - Exit')
	Option=input()
	if(Option == '1'):
		DisplayNewChapters()
	elif(Option == '2'):
		MarkChaptersAsRead()
	elif(Option == '3'):
		exit()
	else:
		print('Invalid input !')
	main()	

#****************************************************************************#
#                               Main Entry Point   	                         #
#****************************************************************************#
if __name__ == '__main__':
	PopulateMangaList()
	main()


