'''
Dependencies:
    Pygoogle: https://code.google.com/p/pygoogle/


Developer: Jheto Xekri
License: LGPL v3
'''

from pygoogle import pygoogle
import sqlite3
import urllib2
import os.path
import sys;

def getUlrContents(urlToGet):
    contents = "";
    
    if(urlToGet.startswith("https") == False): 
        try:
            #contents = contents.decode('utf-8').lower();
            contents = urllib2.urlopen(urlToGet).read()
            contents = contents.lower();
        except():
            print("Error can't get contents from " + urlToGet)
            
    return contents;

def detectCardingTerms(contents):
    cardingTerms = [
        "cvv", "cvv2", "dump", "sell", "track", "transfer", "transfers", "logins", "bank", "fullz", "wu", "cc", "check", 
        "fresh", "info", "bin", "cheap", "credit", "card", "payment", "good", "visa", "mastercard", "discovery", 
        "amex", "dis", "first", "last", "name", "number", "country", "street", "city", "state", "zip", "code", "msr",
        "western", "union", "money", "paypal", "pin", "email", "icq", "rdp", "hacker", "carder", "carding"
    ];
    foundWords = {}
    textWords = contents.split();
    for word in textWords:
        for term in cardingTerms:
            if(word == term):
                if term in foundWords:
                    countWord = foundWords[term]
                    countWord += 1;
                    foundWords[term] = countWord;
                else:
                    foundWords[term] = 1;
    return foundWords;

def getFoundTerms(foundWords):
    terms = [];
    for key, value in foundWords.iteritems() :
        terms.append(key)
    if(len(terms) > 0): return str(str(terms).strip('[]').replace("'","").replace(",",""))
    else: return ""

def countFoundTerms(foundWords):
    terms = 0;
    for key, value in foundWords.iteritems() :
        terms += int(value)
    return terms

#http://www.pythoncentral.io/introduction-to-sqlite-in-python/

def createItem(Url, Terms, Founds):
    item = {'url': Url, 'terms': Terms, 'founds': Founds}
    return item

def sqlite_create(Items):
    con = None
    try:
        filename = 'CarderSites.db'
        if(os.path.isfile(filename)): os.remove(filename)
        con = sqlite3.connect(filename)
        cur = con.cursor()
        cur.execute("DROP TABLE IF EXISTS CarderSites")
        cur.execute("CREATE TABLE CarderSites(id INTEGER PRIMARY KEY AUTOINCREMENT, url TEXT, terms TEXT, founds INTEGER)")
        for item in Items:
            cur.execute("INSERT INTO CarderSites (url, terms, founds) VALUES (?,?,?)", (item["url"], item["terms"], item["founds"]))
        con.commit()    
    except(sqlite3.Error, e):
        print ("Error %s:" % e)
        sys.exit(1)
    finally:
        con.close()

def analyzeUrl(url):
    print("analyze: " + url + "\n")
    html = getUlrContents(url)
    termsDetected = detectCardingTerms(html);
    terms = getFoundTerms(termsDetected);
    founds = countFoundTerms(termsDetected);
    return createItem(url, terms, founds);    

def initSearch(textToSearch, limit):
    g = pygoogle(textToSearch)
    g.pages = 5
    items = []
    c = 0;
    totalResults = g.get_result_count();
    if(totalResults > 0):
        print("Found " + totalResults + " records\n")
        urlResults = g.get_urls();
        for url in urlResults:
            if(c < limit):
                item = analyzeUrl(url);
                items.append(item);
                c+=1
        sqlite_create(items)
    else:
        print("Not found results\n");
        
initSearch("cvv sell", 10)
        
        