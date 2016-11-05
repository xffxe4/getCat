#!/usr/bin/env python
#
###############################################
# Fetching Bluecoat category of a domain 
# Author: bravobingomazinga@gmail.com
# Version: 0.3 (Last updated 2016-10-18)
###############################################
#

import sys
import os
import logging
from optparse import OptionParser,OptionGroup
import urllib
import urllib2
import csv
import string
from HTMLParser import HTMLParser
from BeautifulSoup import BeautifulSoup

LOGGER = logging.getLogger('getCat')
LOGLOC="getCat.log"

# Bluecoat category map ID in this example is from https://bto.bluecoat.com/packetguide/9.2/reference/catmap.htm
# catbook is csv file contains catmap ID, matching category name and example policy
catdic = []
catfile = open("catbook.csv", "rb")
csvParser = csv.reader(catfile)
for ID, Category, Policy in csvParser:
    catdic.append({'ID':ID, 'Category':Category, 'Policy':Policy})

def hex2dec(s):
    return int(s,16)

# appliances query look similar to http://1.2.3.4/1/R/XXXXX-XXXXX/BLU00001/0/GET/http/www.google.com/80/
# replace [replace-this-with-your-query-server] with your appliance's querying address
def checkCategory(x):
    urlToGet="http://[replace-this-with-your-query-server]/BLU00001/0/GET/http/"+x+"/80/"
    r = urllib2.Request(urlToGet)
    htmlresult = urllib2.urlopen(r).read()
    soup = BeautifulSoup(htmlresult)

    try:
        result = soup.domc.renderContents()
    except AttributeError:
        result = soup.dirc.renderContents()

    # for a site under a single category
    catid0 = hex2dec(result)

    # for a site under two categories, for example 'Suspicious' as well as 'Health'
    if len(result) > 2:
        n = 2
        multicat = [result[i:i+n] for i in range(0, len(result), n)]
        catid1 = hex2dec(multicat[0])
        catid2 = hex2dec(multicat[1])
        return catid1, catid2

    return catid0

def main():
    global LOGGER
    global URL

    VERSION = "0.3"
    USAGE = "usage: getCat.py options args"
    parser = OptionParser(USAGE)
    parser.add_option("-d", "--domain", action="store", dest="domain", default=False, type="string", help="Domain to check")
    parser.add_option("-v", "--verbose",action="store_true", dest="verbose", help="Show verbose output")
    parser.add_option("-V", "--version",action="store_true", dest="version", help="Show version and exit")
    (options, args) = parser.parse_args()

    LOGGER.setLevel(logging.DEBUG)
    fh = logging.FileHandler(LOGLOC)
    fh.setLevel(logging.DEBUG)
    ch = logging.StreamHandler()
    ch.setLevel(logging.ERROR)
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s ',  datefmt='%Y/%m/%d %I:%M:%S %p')
    fh.setFormatter(formatter)
    ch.setFormatter(formatter)
    LOGGER.addHandler(fh)
    LOGGER.addHandler(ch)

    LOGGER.info("Example log message")

    if options.version:
            print "getCat", VERSION
            sys.exit()

    if options.domain:
        if options.verbose:
            print "Target domain: "+options.domain
            print "Checking Bluecoat category of the site ... "

        foundID = checkCategory(options.domain)

        if foundID > 200:
            foundID1 = foundID[0]
            foundID2 = foundID[1]
            for count in range(0,len(catdic)):
                if catdic[count]['ID'] == `foundID1`:
                    print "Site: %s, Category: %s, Webaccess Policy: %s" % (options.domain, catdic[count]['Category'], catdic[count]['Policy'])
                    LOGGER.info('Bluecoat Category: '+catdic[count]['Category']+', Webaccess Policy: '+catdic[count]['Policy'])
                    for count in range(0,len(catdic)):
                        if catdic[count]['ID'] == `foundID2`:
                            print "Site: %s, Category: %s, Webaccess Policy: %s" % (options.domain, catdic[count]['Category'], catdic[count]['Policy'])
                            LOGGER.info('Bluecoat Category: '+catdic[count]['Category']+', Webaccess Policy: '+catdic[count]['Policy'])
        
        elif foundID <200:
            for count in range(0, len(catdic)):
                if catdic[count]['ID'] == `foundID`:
                    print "Site: %s, Category: %s, Webaccess Policy: %s" % (options.domain, catdic[count]['Category'], catdic[count]['Policy'])
                    LOGGER.info('Bluecoat Category: '+catdic[count]['Category']+', Webaccess Policy: '+catdic[count]['Policy'])
                                 
        else:
            print "Cannot lookup domain %s .. Please check your Internet connection. " % (options.domain)

    else:
        print "Unknown option. "
        parser.print_help()

if __name__ == "__main__"
    main()
