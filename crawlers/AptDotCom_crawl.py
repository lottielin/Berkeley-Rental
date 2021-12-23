import urllib.request, urllib.error   
from bs4 import BeautifulSoup    
import re     
import pandas as pd

import ssl
ssl._create_default_https_context = ssl._create_unverified_context

# https://www.apartments.com/berkeley-ca/student-housing/2/
#25 per page, 7 page

# ********* DATA contents *********
    # Name
    # Address
    # Link to detail
    # Price range
    # Contact
    # Lat
    # Long

    # Details inside
        # Bedroom num
        # Bathroom num
        # Area

    # {'Varsity Berkeley': ['Varsity Berkeley', '2024 Durant Ave, Berkeley, CA 94704', 'https://www.apartments.com/varsity-berkeley-berkeley-ca/nhlhx2p/', '$4,200 - 6,000', '(844) 281-4205', '2 - 3', '1 - 2', ['715 - 1,100']]}


def main():
    baseurl = "https://www.apartments.com/berkeley-ca/student-housing/"

    #1. crawl main info -- getPriData(baseurl)
    datalist = getPriData(baseurl)
 
    #2. save data -- saveData(datalist, savepath)
    savepath = "aptDotCom_v1.csv"
    saveData(datalist, savepath)

    #3. analyze data -- plotData(datalist)
    

# regular expressions
findName = re.compile(r'<span class="js-placardTitle title">(.*)</span>')  
findAddress = re.compile(r'<div class="property-address js-url" title=".*">(.*)</div>')
findSLink = re.compile("href=\"(.+?)\"")
findPrice = re.compile(r'<p class="property-pricing">(.*)</p>')
#findContact= re.compile(r'<a class="phone-link js-phone" href=".*"><i class="storyicon comMobileStoryIcon"></i><span>(.*)</span></a>')
findBedroom= re.compile(r'<p class="rentInfoDetail">(.*?) bd</p>')
findBathroom= re.compile(r'<p class="rentInfoDetail">(.*) ba</p>')
findArea= re.compile(r'<p class="rentInfoDetail">(.*) sq ft</p>')
findLat = re.compile(r'<meta property="place:location:latitude" content="(.*)">')
findLong = re.compile(r'<meta property="place:location:longitude" content="(.*)">')


def getPriData(baseurl):
    pageNum = 7
    datalist = {}
    # set constant pageNum for now
    for i in range(1):
        url = baseurl + str(i) + "/"
        html = askURL(url)
        soup = BeautifulSoup(html, "html.parser")

        for li in soup.find_all("li", class_ = "mortar-wrapper"):
            data = []
            li = str(li)
            
            name = re.findall(findName, li)[0]
            data.append(name)
            address = re.findall(findAddress, li)[0]
            data.append(address)
            sLink = re.findall(findSLink, li)[0]
            data.append(sLink)
            price = re.findall(findPrice, li)[0]
            data.append(price)
            contact = re.findall(r"<span>(\(\d+\)\s\d+\-\d+)</span>", li)[0]
            data.append(contact)

            # long
            # lat

            #2. crawl detail info
            detail_html = askURL(sLink)
            soup = BeautifulSoup(detail_html, "html.parser")
            
            lat = re.findall(findLat, detail_html)[0]
            data.append(lat)
            long = re.findall(findLong, detail_html)[0]
            data.append(long)

            for ul in soup.find_all("ul", class_="priceBedRangeInfo"):
                ul = str(ul)

                bedNum = re.findall(findBedroom, ul)[0]
                data.append(bedNum)
                bathNum = re.findall(findBathroom, ul)[0]
                data.append(bathNum)
                area = re.findall(findArea, ul)
                data.append(area)

            datalist[name] = data 

    #print(datalist['Varsity Berkeley'])
    return datalist

def askURL(url):
    """
    Retrieve raw html
    :param url: base url
    :return :html of page
    """
    head = {"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.114 Safari/537.36"}
    request = urllib.request.Request(url, headers=head)
    html = ""
    try:
        response = urllib.request.urlopen(request)
        html = response.read().decode("utf-8")
    except urllib.error.URLError as e:
        if hasattr(e, "code"):
            print(e.code)
        if hasattr(e, "reason"):
            print(e.reason) 
    return html


def pltData(datalist):
    pass


def saveData(datalist, savepath):
    data_columns = ['Name', 'Address', 'Link', 'Price', 'Contact', 'Latitude', 'Longitude', 'Bedroom Number', 'Bathroom Number', 'Area']
    """ try:
        with open(savepath , 'w') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=data_columns)
            writer.writeheader()
            for house in datalist:
                writer.writerow(house)
    except Exception as e:
        print(e) """
    
    pd.DataFrame.from_dict(data=datalist, orient='index').to_csv(savepath, header=data_columns)


if __name__ == '__main__':
    main()
    print('Crawled Berkeley housing data from Apartment.com!')