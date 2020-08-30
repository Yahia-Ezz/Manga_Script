from dataclasses import dataclass
from termcolor import colored
import requests
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
Website.append('https://mangakakalot.com/search/story/')
Website.append('https://manganelo.com/manga/')
Website.append('https://mangatx.com/manga/')

#Clean Regex '(?<=.)\^\D+(?!\^)\w+\^\w+'

Regex = list()
Regex.append('(?<=\<a rel=\"nofollow\" href=\"https:\/\/manganelo\.com\/chapter\/).+?(?=\/chapter_)')
Regex.append('(?<=\\n<a href=\"https:\/\/mangakakalot\.com\/chapter\/).+?(?=\/chapter_)')
Regex.append("(?<=genre-40\\\\'>).+?(?=</a>)|(?<=genre-44\\\\'>).+?(?=</a>)")


FormatChar = list()
FormatChar.append({' ':'_','\'':'',',':'','!':''})
FormatChar.append({' ':'_','\'':'',',':'','!':''})
FormatChar.append({' ':'_','\'':'',',':'','!':''})



@dataclass
class MyMangaStruct(object):
	def __init__(self,Name,ChapterRead,Origin,Website,WebsiteKey,NewChapter,Status):
		self.Name = Name
		self.ChapterRead = ChapterRead
		self.Origin = Origin
		self.WebsiteKey = WebsiteKey
		self.Website = Website
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
				MangaList.append(MyMangaStruct(Tmp[0],Tmp[1],Tmp[2],Tmp[3],Tmp[4],'\n','',))



def GetNewChaptersData(n):
	if( MangaList[n].Origin == None ):
		MangaList[n].WebsiteKey = GetSearchKey(n)
		print(MangaList[n].WebsiteKey)
		print(GetOrigin(n))

def GetSearchKey(n):
	try:
		if(FetchRawHtmlPage(UrlFormater(MangaList[n].Name,'GetKey')) == "OK"):
			Data = re.search(Regex[0],str(HmtlPage))
	except:
			Data[0]=("No Key Found !")
	
	return Data[0]

def GetOrigin(n):
	try:
		if(FetchRawHtmlPage(UrlFormater(MangaList[n].WebsiteKey,'GetOrigin')) == "OK"):
			Data = re.search(Regex[2],str(HmtlPage))
	except:
		print("No Origin Found ")
	if Data is None:
		return 'Uknown'
	return Data[0]


def FetchRawHtmlPage(URL):
	global HmtlPage
	try:
		req = urllib.request.Request( URL , headers={'User-Agent': 'Mozilla/5.0'}) 
		response = urllib.request.urlopen(req)
		if(response.getcode() == 200):
			HmtlPage = response.read()
			response.close()
			return "OK"
	except:
		return "NOK"

def UrlFormater(urlText,index):
	if (index == 'GetKey'):
		i=0
	elif(index == 'GetOrigin'):
		i=1
	urlText = "".join([FormatChar[i].get(c, c) for c in urlText])
	urlText = Website[i] + urlText
	return urlText

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
	PopulateMangaList()
#	for i in range (len(MangaList)):
#		GetNewChaptersData(i)
	GetNewChaptersData(3)
	
if __name__ == '__main__':
	main()

