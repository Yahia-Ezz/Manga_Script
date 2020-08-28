from dataclasses import dataclass
import urllib.request
import re
from termcolor import colored
import tkinter as tk 
import ctypes
import os

#user32 = ctypes.windll.user32

#screensize = user32.GetSystemMetrics(0), user32.GetSystemMetrics(1)
#(?<=\\n<a rel="nofollow" href="https:\/\/manganelo\.com\/manga\/).+(?=">\\n<img)
Website = []
Website.append("https://mangakakalot.com/search/story/")
Website.append("https://mangatx.com/manga/")

DataFile = "Kissmanga_Bookmarks.txt"

MyMangaList = []
HTML_return = str()
	
@dataclass
class MyMangaStruct(object):
	def __init__(self,MangaName,ChapterRead,MangaWebSite,MangaWebSiteKey,NewChapter,Status):
		self.MangaName = MangaName
		self.ChapterRead = ChapterRead
		self.MangaWebSite = MangaWebSite
		self.MangaWebSiteKey = MangaWebSiteKey
		self.NewChapter = NewChapter
		self.Status  = Status

		
def CheckNewEntriesAndNewChapters(n):
	URL = Website[0]+MyMangaList[n].MangaName.replace(' ','_').replace('\'','_').replace(',','').replace('!','')+"/"
	try:
		req = urllib.request.Request(URL,headers={'User-Agent': 'Mozilla/5.0'})
		response = urllib.request.urlopen(req)
	
		if(response.getcode() == 200):
			global HTML_return
			HTML_return = response.read()
			response.close()
			Flag="OK"
			return Flag
	except:
		Flag="NOK"
		return Flag

def GetLatestChapter(n):
	Check = CheckNewEntriesAndNewChapters(n)
	if "OK" == Check:
		global HTML_return
		the_page = HTML_return
		if (MyMangaList[n].MangaWebSiteKey == 'None\n'):
			SearchKey = re.search(r'(?<=\<a rel=\"nofollow\" href=\"https:\/\/manganelo\.com\/chapter\/).+?(?=\/chapter_)',str(the_page))
			if( str(SearchKey) == 'None'):
				SearchKey = re.search(r'(?<=\\n<a href=\"https:\/\/mangakakalot\.com\/chapter\/).+?(?=\/chapter_)',str(the_page))
			MyMangaList[n].MangaWebSiteKey = str(SearchKey[0]) + '\n'
		
		MyMangaList[n].MangaWebSite = "https://mangakakalot.com/cahpter"
		NewChapter = re.search(r'(?<=rel=\"nofollow\" href=\"https:\/\/manganelo\.com\/chapter\/'+str(MyMangaList[n].MangaWebSiteKey).rstrip('\n')+'\\/chapter_).+?(?=\" title=\")',str(the_page))
		if ( str(NewChapter) == 'None'):
			NewChapter = re.search(r'(?<=a href=\"https:\/\/mangakakalot\.com\/chapter\/'+str(MyMangaList[n].MangaWebSiteKey).rstrip('\n')+'\\/chapter_).+?(?=\" title=\")',str(the_page))
			
		MyMangaList[n].NewChapter = NewChapter[0]
		UpdateStatus(n)
		if MyMangaList[n].Status == 1:
			if( (float(MyMangaList[n].NewChapter)-float(MyMangaList[n].ChapterRead) > 0 )):
				color = 'green'
			else:
				color = 'red'
			print(str(n) + " - " + MyMangaList[n].MangaName + " : " + colored(str( float(MyMangaList[n].NewChapter)-float(MyMangaList[n].ChapterRead) ),color)+ " New chapters.")
		else:
		print("Invalid Manga Link"+str(MyMangaList[n].MangaName.rstrip('\n')))

def UpdateStatus(n):
	if(float(MyMangaList[n].ChapterRead) != float(MyMangaList[n].NewChapter)):
		MyMangaList[n].Status = 1
	else:
		MyMangaList[n].Status = 0

def PopulateMangaList():
	with open(DataFile, "r") as my_file:
		for line in my_file:
			Tmp=line.split('^')
			if(len(Tmp) == 1):
				MyMangaList.append(MyMangaStruct(Tmp[0].rstrip("\n"),str(0),None,None,'\n',''))
			elif(len(Tmp) == 2):
				MyMangaList.append(MyMangaStruct(Tmp[0],Tmp[1].rstrip("\n"),None,None,'\n',''))
			else:	
				MyMangaList.append(MyMangaStruct(Tmp[0],Tmp[1],Tmp[2],Tmp[3],'\n',''))

def UpdateMangaFile():
	MyMangaFile = open(DataFile,"r")
	MyMangaLines = MyMangaFile.readlines()
	Tmp=""	
	i=0
	global MyMangaList
	for Line in (MyMangaLines):
		Tmp = str(MyMangaList[i].MangaName) + "^" + str(MyMangaList[i].ChapterRead) + "^"  
		Tmp += str(MyMangaList[i].MangaWebSite) + "^"+ str(MyMangaList[i].MangaWebSiteKey.rstrip('\n')) 
		Tmp += "^" + str(MyMangaList[i].NewChapter)+"\n"
		MyMangaLines[i] = Tmp
		i += 1
	
	MyMangaFile = open(DataFile,"w")
	MyMangaFile.writelines(MyMangaLines)
	MyMangaFile.close()

def main():
	PopulateMangaList()
	#GetLatestChapter(49)
	for i in range (len(MyMangaList)):
		GetLatestChapter(i)
	UpdateMangaFile()

if __name__ == '__main__':
	main()

