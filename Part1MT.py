from multiprocessing.dummy import Pool as ThreadPool
from pathlib import Path
import os
import re
import json
from bs4 import BeautifulSoup, Comment

class Posting:
    def __init__(self, docID, freqCount):
        self.docID = docID
        self.freqCount = freqCount

    def incFreq(self):
        self.freqCount += 1

    def show(self):
        return [self.docID, self.freqCount]

def getAllFilePaths(directoryPath: str) -> list:
    listFilePaths = list()
    hashTableIDToUrl = dict()

    # create list of all subdirectories that we need to process
    pathParent = Path(directoryPath)
    directory_list = [(pathParent / dI) for dI in os.listdir(directoryPath) if
                      Path(Path(directoryPath).joinpath(dI)).is_dir()]

    iDocID = 0

    for directory in directory_list:
        #print(str(directory))
        for files in Path(directory).iterdir():
            if files.is_file():
                fullFilePath = directory / files.name
                listFilePaths.append([iDocID, str(fullFilePath)])
                hashTableIDToUrl[iDocID] = str(fullFilePath)
                iDocID += 1

    # write json file that maps the docID's to file path urls
    writeHashTableToDisk(hashTableIDToUrl)

    return listFilePaths


def tokenize(fileItem: list) -> dict:
    filePath = fileItem[1]
    docID = fileItem[0]

    with open(filePath, 'r') as content_file:
        textContent = content_file.read()

        jsonOBJ = json.loads(textContent)
        url = jsonOBJ["url"]
        htmlContent = jsonOBJ["content"]

        tokenDict = dict()

        # initialize object and pass in html
        soup = BeautifulSoup(htmlContent, 'html.parser')

        # removes comments from text
        for tag in soup(text=lambda text: isinstance(text, Comment)):
            tag.extract()

        # removes javascript and css from text
        for element in soup.findAll(['script', 'style']):
            element.extract()

        # add all tokens found from html response with tags removed
        varTemp = soup.get_text()

        listTemp = re.split(r"[^a-z0-9']+", varTemp.lower())
        for word in listTemp:
            if (len(word) == 0):  # ignore empty strings
                continue
            if word in tokenDict:
                tokenDict.get(word).incFreq()
            else:
                tokenDict[word] = Posting(docID, 1)

        # write partial indexes to text files ("store on disk")
        buildPartialIndex(tokenDict)
        # merge later

        # # change the code here to save Postings (tdif, frequency count, linkedList of DocID's, etc)
        # return tokenDict


# write json file that maps the docID's to file path urls
def writeHashTableToDisk(hashtable: dict) -> None:
    if not os.path.exists("partial_indexes"):
        Path("partial_indexes").mkdir()
    with open(os.path.join("partial_indexes", "hashtable.txt"), "w+") as hash:
        hash.write(json.dumps(hashtable))


def buildPartialIndex(tokenDict):
    # make subdirectory for partial indexes
    if not os.path.exists("partial_indexes"):
        Path("partial_indexes").mkdir()

    # write text files to store inndexing data for merging later
    with open(os.path.join("partial_indexes", "index.txt"), "a") as partialIndex:
        for key in sorted(tokenDict):
            partialIndex.write(key + " : " + str(tokenDict.get(key).show()) + '\n');


def parseJSONFiles(directoryPath: str) -> int:
    listFilePaths = getAllFilePaths(directoryPath)

    DOC_NUM = len(listFilePaths)    #number of files we will tokenize

    # https://stackoverflow.com/questions/2846653/how-can-i-use-threading-in-python
    # Make the Pool of workers
    pool = ThreadPool(20)

    # Each worker get a directory from list above, and begin tokenizing all json files inside
    results = pool.map(tokenize, listFilePaths)

    # for key in results[0]:
    # print(key, " : ", results[0].get(key).show())

    # Close the pool and wait for the work to finish
    pool.close()
    pool.join()

    return

if __name__ == '__main__':
    # Aljon
    #folderPath = "C:\\Users\\aljon\\Documents\\CS121_InvertedIndex\\DEV"

    # William
    folderPath = "C:\\Anaconda3\\envs\\Projects\\DEV"

    iDocsCount = parseJSONFiles(folderPath)
    print("Number of docs = ", iDocsCount)
    print("-----DONE!-----")
