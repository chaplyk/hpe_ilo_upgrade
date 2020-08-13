#!/usr/bin/python
import re, requests, pexpect
import time
# ignore HTTPS warnings
from requests.packages.urllib3.exceptions import InsecureRequestWarning
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

# text colour
CRED = '\033[91m'
CGREEN = '\033[92m'
CEND = '\033[0m'

# URL to iLO firmware (f.e. http://127.0.0.1/ilo4_273.bin"
url=""
# get version number from url
latest_version=url.split("_")[1].split(".")[0]
latest_version=latest_version[:1] + '.' + latest_version[1:]

#function that upgrades iLO firmware
def ilo_upgrade(ip, username, password):
    child = pexpect.spawn('ssh -o "StrictHostKeyChecking no" ' + username + '@' + ip)
    child.expect(username + "@" + ip + "'s password:")
    child.sendline(password)
    time.sleep(5)
    child.expect('</>hpiLO-> ')
    child.timeout=600
    child.sendline('load map1/firmware1 -source ' + url)
    child.expect('Resetting iLO.')
    return child.before

#function that checks current iLO version
def ilo_version(ip):
    r1=requests.get('https://' + ip + '/xmldata?item=All', verify=False)
    for search_line in r1.text.splitlines():
            if re.search("FWRI",search_line):
                version=search_line.split(">")[1].split("<")[0]
                return version

#check current iLO version
with open('ilo.csv') as f:
    list=[]
    for line in f:
        x=line.split(",")
        ip=x[0]
        username=x[1]
        password=x[2].replace("\n", "").replace("\r", "")
        current_version=ilo_version(ip)
        if current_version != latest_version:
            print(CRED + ip + " has outdated iLO version: " + current_version + CEND)
            list.append([ip, username, password])

#promt to upgrade iLO
print ("There are " + str(len(list)) + " iLO that have outdated firmware. Would you like to upgrade them to " + latest_version + "? (yes/no)")
if raw_input().lower() in {'yes','y'}:
    for item in list:
        ip=item[0]
        username=item[1]
        password=item[2]
        print (CGREEN + "Upgrading " + ip + ":" + CEND)
        print ilo_upgrade(ip, username, password)

#after checks
for item in list:
    ip=item[0]
    username=item[1]
    password=item[2]
    time.sleep(60)
    upgraded_version=ilo_version(ip)
    if upgraded_version != latest_version:
        print(CRED + "There was an issue during iLO upgrade for " + ip + ". Current version is " + upgraded_version + CEND)
