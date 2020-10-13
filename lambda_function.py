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
from prettytable import PrettyTable



config = configparser.ConfigParser()
config.read("./config.ini")
strProdURL      = config.get("vmcConfig", "strProdURL")
strCSPProdURL   = config.get("vmcConfig", "strCSPProdURL")
Refresh_Token   = config.get("vmcConfig", "refresh_Token")
ORG_ID          = config.get("vmcConfig", "org_id")
SDDC_ID         = config.get("vmcConfig", "sddc_id")
expected_host   = config.get("vmcConfig", "expected_host")
to_reduced_host = 0



#print("The SDDC " + str(SDDC_ID) + " in the " + str(ORG_ID) + " ORG will be scaled down.")

def getAccessToken(myKey):
    params = {'refresh_token': myKey}
    headers = {'Content-Type': 'application/json'}
    response = requests.post('https://console.cloud.vmware.com/csp/gateway/am/api/auth/api-tokens/authorize', params=params, headers=headers)
    jsonResponse = response.json()
    access_token = jsonResponse['access_token']
    return access_token

#-------------------- Show hosts in an SDDC
def getCDChosts(sddcID, tenantid, sessiontoken):

    myHeader = {'csp-auth-token': sessiontoken}
    myURL = strProdURL + "/vmc/api/orgs/" + tenantid + "/sddcs/" + sddcID

    response = requests.get(myURL, headers=myHeader)

    # grab the names of the CDCs
    jsonResponse = response.json()

    # get the vC block (this is a bad hack to get the rest of the host name
    # shown in vC inventory)
    cdcID = jsonResponse['resource_config']['vc_ip']
    cdcID = cdcID.split("vcenter")
    cdcID = cdcID[1]
    cdcID = cdcID.split("/")
    cdcID = cdcID[0]

    # get the hosts block
    hosts = jsonResponse['resource_config']['esx_hosts']
    table = PrettyTable(['Name', 'Status', 'ID'])
    for i in hosts:
        hostName = i['name'] + cdcID
        table.add_row([hostName, i['esx_state'], i['esx_id']])
    print(table)
    return
#print ("Hosts are in the cluster: " + str(esx_hosts))


#def removeCDChosts(hosts, org_id, sddc_id, sessiontoken):
#    myHeader = {'csp-auth-token': sessiontoken}
#    myURL = strProdURL + "/vmc/api/orgs/" + org_id + "/sddcs/" + sddc_id + "/esxs"
#    strRequest = {"num_hosts": hosts}
#    response = requests.delete(myURL, json=strRequest, headers=myHeader)
#    print(str(hosts) + " host(s) have been removed to the SDDC")
#    print(response)
#    return




# --------------------------------------------
# ---------------- Main ----------------------
# --------------------------------------------

def lambda_handler(event, context):
    session_token = getAccessToken(Refresh_Token)
    getCDChosts(sddc_ID, refresh_token, sessiontoken)
    return
