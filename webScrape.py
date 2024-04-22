from urllib.request import urlopen
url = "https://www.rhymezone.com/r/rhyme.cgi?Word=%s&org1=syl&org2=l&org3=y&typeofrhyme=nry"%'green'
page = urlopen(url)
html = page.read().decode("utf-8")
startIndex=html.find('API_RESULTS')
stopIndex=html.find('var CACHED_API_URL')
goodLine=html[startIndex:stopIndex]
exec(goodLine)
#print(API_RESULTS)

for i in range(1,10):
  print(API_RESULTS[i]['word'])