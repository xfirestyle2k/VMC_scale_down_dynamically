"""

Scheduled Auto-Scale for VMware Cloud on AWS


You can install python 3.6 from https://www.python.org/downloads/windows/

You can install the dependent python packages locally (handy for Lambda) with:
pip install requests -t . --upgrade
pip install configparser -t . --upgrade

"""

import requests                         # need this for Get/Post/Delete
import configparser                     # parsing config file
import time
import json

config = configparser.ConfigParser()
config.read("./config.ini")
strProdURL      = config.get("vmcConfig", "strProdURL")
strCSPProdURL   = config.get("vmcConfig", "strCSPProdURL")
Refresh_Token   = config.get("vmcConfig", "refresh_Token")
ORG_ID          = config.get("vmcConfig", "org_id")
SDDC_ID         = config.get("vmcConfig", "sddc_id")
expected_host   = config.get("vmcConfig", "expected_host")



print("The SDDC " + str(SDDC_ID) + " in the " + str(ORG_ID) + " ORG will be scaled down.")

def getAccessToken(myKey):
    params = {'refresh_token': myKey}
    headers = {'Content-Type': 'application/json'}
    response = requests.post('https://console.cloud.vmware.com/csp/gateway/am/api/auth/api-tokens/authorize', params=params, headers=headers)
    jsonResponse = response.json()
    access_token = jsonResponse['access_token']
    return access_token

def getSDDCS(tenantid, sessiontoken):           # get current hostcount and return it
    myHeader = {'csp-auth-token': sessiontoken}
    myURL = strProdURL + "/vmc/api/orgs/" + tenantid + "/sddcs"
    response = requests.get(myURL, headers=myHeader)
    jsonResponse = response.json()
    orgtable = PrettyTable(['OrgID'])
    orgtable.add_row([tenantid])
    print(str(orgtable))
    table = PrettyTable(['Name', 'Cloud', 'Status', 'Hosts', 'ID'])
    for i in jsonResponse:
        hostcount = 0
        myURL = strProdURL + "/vmc/api/orgs/" + tenantid + "/sddcs/" + i['id']
        response = requests.get(myURL, headers=myHeader)
        mySDDCs = response.json()
        if mySDDCs['resource_config']:
            hosts = mySDDCs['resource_config']['esx_hosts']
            if hosts:
                for j in hosts:
                    hostcount = hostcount + 1
        table.add_row([i['name'], i['provider'],i['sddc_state'], hostcount, i['id']])
    return hostcount

def toreducehosts(hostcount, expected_host):    # hostcount - expected_hosts
    to_reduce = hostcount - expected_host

    print(str(to_reduce) + " has to be remove")
    return to_reduce

def removeCDChosts(to_reduce, org_id, sddc_id, sessiontoken):     #reduce hosts
    myHeader = {'csp-auth-token': sessiontoken}
    myURL = strProdURL + "/vmc/api/orgs/" + org_id + "/sddcs/" + sddc_id + "/esxs"
    strRequest = {"num_hosts": to_reduce}
    response = requests.delete(myURL, json=strRequest, headers=myHeader)
    print(str(to_reduce) + " host(s) have been removed to the SDDC")
    print(response)
    return


# --------------------------------------------
# ---------------- Main ----------------------
# --------------------------------------------

def lambda_handler(event, context):
    session_token = getAccessToken(Refresh_Token)
    hostcount = getSDDCS()
    removeCDChosts(to_reduce, ORG_ID, SDDC_ID, session_token)
    return
