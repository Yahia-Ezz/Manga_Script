from dataclasses import dataclass
from termcolor import colored
import urllib.request
import re

# import os
# import tkinter as tk 
# user32 = ctypes.windll.user32

# screensize = user32.GetSystemMetrics(0), user32.GetSystemMetrics(1)
# (?<=\\n<a rel="nofollow" href="https:\/\/manganelo\.com\/manga\/).+(?=">\\n<img)
DataFile = "Kissmanga_Bookmarks.txt"

global MangaList,HmtlPage
MangaList= list()
HmtlPage = str()

Website = list()
Website.append('https://mangadex.org/search?tag_mode_exc=any&tag_mode_inc=all&title=')
Website.append('https://mangakakalot.com/search/story/')
Website.append('https://mangatx.com/manga/')

#Clean Regex '(?<=.)\^\D+(?!\^)\w+\^\w+'

Regex = list()
Regex.append('(?<=<div><span class=\"rounded flag flag-)..(?=\")')
Regex.append('(?<=\<a rel=\"nofollow\" href=\"https:\/\/manganelo\.com\/chapter\/).+?(?=\/chapter_)')
Regex.append('(?<=\\n<a href=\"https:\/\/mangakakalot\.com\/chapter\/).+?(?=\/chapter_)')

FormatChar = []
FormatChar.append({' ':'%20','\'':'%27',',':'%2C'})	

@dataclass
class MyMangaStruct(object):
	def __init__(self,Name,ChapterRead,Origin,Website,WebsiteKey,NewChapter,Status):
		self.Name = Name
		self.ChapterRead = ChapterRead
		self.Origin = Origin
		self.Website = Website
		self.WebsiteKey = WebsiteKey
		self.NewChapter = NewChapter
		self.Status  = Status

def PopulateMangaList():
	with open(DataFile, "r") as my_file:
		for line in my_file:
			Tmp=line.split('^')
			if(len(Tmp) == 1):
				MangaList.append(MyMangaStruct(Tmp[0].rstrip("\n"),str(0),None,None,'\n','',''))
			elif(len(Tmp) == 2):
				MangaList.append(MyMangaStruct(Tmp[0],Tmp[1].rstrip("\n"),None,None,'\n','',''))
			else:	
				MangaList.append(MyMangaStruct(Tmp[0],Tmp[1],Tmp[2],Tmp[3],'\n','',''))

def GetLatestChapter(n):
	if MangaList[n].Origin is None:
		MangaList[n].Origin = FetchMangaOrigin(n,0)
	# if "OK" == FetchRawHtmlPage(0,n):
	# 	if (MangaList[n].WebsiteKey == 'None\n'):
	# 		SearchKey = re.search(rKeyRegex[0],str(HmtlPage))
	# 		if( SearchKey == 'None'):
	# 			SearchKey = re.search(rKeyRegex[1],str(HmtlPage))
	# 		MangaList[n].WebsiteKey = str(SearchKey[0]+'\n') 
		
	# 	MangaList[n].Website = "https://mangakakalot.com/cahpter"
	# 	NewChapter = re.search(r'(?<=rel=\"nofollow\" href=\"https:\/\/manganelo\.com\/chapter\/'+str(MangaList[n].WebsiteKey).rstrip('\n')+'\\/chapter_).+?(?=\" title=\")',str(HmtlPage))
	# 	if ( str(NewChapter) == 'None'):
	# 		NewChapter = re.search(r'(?<=a href=\"https:\/\/mangakakalot\.com\/chapter\/'+str(MangaList[n].WebsiteKey).rstrip('\n')+'\\/chapter_).+?(?=\" title=\")',str(HmtlPage))
			
	# 	MangaList[n].NewChapter = NewChapter[0]
	# 	UpdateStatus(n)
	# 	if MangaList[n].Status == 1:
	# 		if( (float(MangaList[n].NewChapter)-float(MangaList[n].ChapterRead) > 0 )):
	# 			color = 'green'
	# 		else:
	# 			color = 'red'
	# 		print(str(n) + " - " + MangaList[n].Name + " : " + colored(str( float(MangaList[n].NewChapter)-float(MangaList[n].ChapterRead) ),color)+ " New chapters.")
	# else:
	# 	print("Invalid Manga Link"+str(MangaList[n].Name.rstrip('\n')))

def FetchMangaOrigin(n,FormatIndex):
	global HmtlPage
	if  FetchRawHtmlPage(str(UrlFormater(MangaList[n].Name,FormatIndex))) == "OK":
		Origin = re.search(rf'%{Regex[0]}',str(HmtlPage))
		
		print(Origin)	
#	else:
#		print("NotFound Origin")
	#print(Origin)
	#return Origin[0]

def FetchRawHtmlPage(URL):
	global HmtlPage
	try:
		req = urllib.request.Request(URL,headers={'User-Agent': 'Mozilla/5.0'})
		response = urllib.request.urlopen(req)
	
		if(response.getcode() == 200):
			HmtlPage = response.read()
			response.close()
			print(str(HmtlPage))
			return "OK"
	except:
		return "NOK"


def UrlFormater(urlText,FormatIndex):
    global FormatChar,MangaList,Website
    urlText = "".join([FormatChar[FormatIndex].get(c, c) for c in urlText])
    urlText = Website[FormatIndex] + urlText
    return urlText
		


def UpdateStatus(n):
	if(float(MangaList[n].ChapterRead) != float(MangaList[n].NewChapter)):
		MangaList[n].Status = 1
	else:
		MangaList[n].Status = 0



def UpdateMangaFile():
	MyMangaFile = open(DataFile,"r")
	MyMangaLines = MyMangaFile.readlines()
	Tmp=""	
	i=0
	global MangaList
	for Line in (MyMangaLines):
		Tmp = str(MangaList[i].Name) + "^" + str(MangaList[i].ChapterRead) + "^"  
		Tmp += str(MangaList[i].Website) + "^"+ str(MangaList[i].WebsiteKey.rstrip('\n')) 
		Tmp += "^" + str(MangaList[i].NewChapter)+"\n"
		MyMangaLines[i] = Tmp
		i += 1
	
	MyMangaFile = open(DataFile,"w")
	MyMangaFile.writelines(MyMangaLines)
	MyMangaFile.close()

def main():
	global MangaList
	PopulateMangaList()
	#GetLatestChapter(49)
	#for i in range (len(MangaList)):
	#	GetLatestChapter(i)
	#UpdateMangaFile()
	GetLatestChapter(2)
	
if __name__ == '__main__':
	main()

