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

MangaList = []
HmtlPage = str()

WebSite = list()
WebSite.append('https://mangakakalot.com/search/story/')
WebSite.append('https://mangatx.com/manga/')

Regex = list()
Regex.append('(?<=\<a rel=\"nofollow\" href=\"https:\/\/manganelo\.com\/chapter\/).+?(?=\/chapter_)')
Regex.append('(?<=\\n<a href=\"https:\/\/mangakakalot\.com\/chapter\/).+?(?=\/chapter_)')
Regex.append('')

	
@dataclass
class MyMangaStruct(object):
	def __init__(self,Name,ChapterRead,WebSite,WebSiteKey,NewChapter,Status):
		self.Name = Name
		self.ChapterRead = ChapterRead
		self.WebSite = WebSite
		self.WebSiteKey = WebSiteKey
		self.NewChapter = NewChapter
		self.Status  = Status

		
def CheckNewEntriesAndNewChapters(n):
	global HmtlPage		
	URL = WebSite[0]+MangaList[n].Name.replace(' ','_').replace('\'','_').replace(',','').replace('!','')+"/"
	try:
		req = urllib.request.Request(URL,headers={'User-Agent': 'Mozilla/5.0'})
		response = urllib.request.urlopen(req)
	
		if(response.getcode() == 200):
			HmtlPage = response.read()
			response.close()
			return "OK"
	except:
		return "NOK"

def GetLatestChapter(n):
	global HmtlPage
	if "OK" == CheckNewEntriesAndNewChapters(n):
		if (MangaList[n].WebSiteKey == 'None\n'):
			SearchKey = re.search(rRegex[0],str(HmtlPage))
			if( SearchKey == 'None'):
				SearchKey = re.search(rRgex[1],str(HmtlPage))
			MangaList[n].WebSiteKey = str(SearchKey[0]+'\n') 
		
		MangaList[n].WebSite = "https://mangakakalot.com/cahpter"
		NewChapter = re.search(r'(?<=rel=\"nofollow\" href=\"https:\/\/manganelo\.com\/chapter\/'+str(MangaList[n].WebSiteKey).rstrip('\n')+'\\/chapter_).+?(?=\" title=\")',str(HmtlPage))
		if ( str(NewChapter) == 'None'):
			NewChapter = re.search(r'(?<=a href=\"https:\/\/mangakakalot\.com\/chapter\/'+str(MangaList[n].WebSiteKey).rstrip('\n')+'\\/chapter_).+?(?=\" title=\")',str(HmtlPage))
			
		MangaList[n].NewChapter = NewChapter[0]
		UpdateStatus(n)
		if MangaList[n].Status == 1:
			if( (float(MangaList[n].NewChapter)-float(MangaList[n].ChapterRead) > 0 )):
				color = 'green'
			else:
				color = 'red'
			print(str(n) + " - " + MangaList[n].Name + " : " + colored(str( float(MangaList[n].NewChapter)-float(MangaList[n].ChapterRead) ),color)+ " New chapters.")
	else:
		print("Invalid Manga Link"+str(MangaList[n].Name.rstrip('\n')))

def UpdateStatus(n):
	if(float(MangaList[n].ChapterRead) != float(MangaList[n].NewChapter)):
		MangaList[n].Status = 1
	else:
		MangaList[n].Status = 0

def PopulateMangaList():
	with open(DataFile, "r") as my_file:
		for line in my_file:
			Tmp=line.split('^')
			if(len(Tmp) == 1):
				MangaList.append(MyMangaStruct(Tmp[0].rstrip("\n"),str(0),None,None,'\n',''))
			elif(len(Tmp) == 2):
				MangaList.append(MyMangaStruct(Tmp[0],Tmp[1].rstrip("\n"),None,None,'\n',''))
			else:	
				MangaList.append(MyMangaStruct(Tmp[0],Tmp[1],Tmp[2],Tmp[3],'\n',''))

def UpdateMangaFile():
	MyMangaFile = open(DataFile,"r")
	MyMangaLines = MyMangaFile.readlines()
	Tmp=""	
	i=0
	global MangaList
	for Line in (MyMangaLines):
		Tmp = str(MangaList[i].Name) + "^" + str(MangaList[i].ChapterRead) + "^"  
		Tmp += str(MangaList[i].WebSite) + "^"+ str(MangaList[i].WebSiteKey.rstrip('\n')) 
		Tmp += "^" + str(MangaList[i].NewChapter)+"\n"
		MyMangaLines[i] = Tmp
		i += 1
	
	MyMangaFile = open(DataFile,"w")
	MyMangaFile.writelines(MyMangaLines)
	MyMangaFile.close()

def main():
	PopulateMangaList()
	#GetLatestChapter(49)
	for i in range (len(MangaList)):
		GetLatestChapter(i)
	UpdateMangaFile()

if __name__ == '__main__':
	main()

