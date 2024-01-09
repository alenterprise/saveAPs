import requests
import csv
import sys
import json


################## OV IP + USER/PASSWORD ##############


OmniVistaIP = "172.26.10.131"
userOV = "admin"
passwordOV = "switch"


#######################################################


requests.packages.urllib3.disable_warnings()

url = "https://"+OmniVistaIP+"/rest-api/login"  # Remplacez l'URL par celle de l'API que vous souhaitez appeler
url2 = "https://"+OmniVistaIP+"/api/devices?fieldSetName=discovery" # GET, Permet de recuperer l'instance ID d'une AP.(=uid)
url3 = "https://"+OmniVistaIP+"/api/discoverylite/gettriggerid" # GET, Permet de recuperer l'id du "Save To Running"
url4 = "https://"+OmniVistaIP+"/api/discoverylite/configdeviceoperations/triggeroperation" # POST, permet d'envoyer un save to running à une ou plusieurs AP


headers = {
    "Content-Type": "application/json"  # Spécifiez le type de contenu de la requête
}

data = {
    "userName": userOV,
    "password": passwordOV
}

response = requests.post(url, headers=headers, json=data, verify=False)

if response.status_code == 200:
    data = response.json()
    token= response.json().get("accessToken")
    #print("token vaut : ",token)
else:
    print("Erreur lors de l'appel de l'API :", response.status_code)



headers2 = {
    "Content-Type": "application/json",  # Spécifiez le type de contenu de la requête
    'Authorization': "Bearer {}".format(token)
}

response = requests.get(url2, headers=headers2, verify=False)
data = response.json()

count_ap = 0

for item in data['response']:
    if 'ipAddress' in item:
        count_ap += 1

response= requests.get(url3, headers=headers2, verify=False)
json_response = response.json()
data_value = json_response.get("response", {}).get("data") # Recupere le trigger id qui vaut Save to Running


body = {
    "TriggerConfigDeviceOperationsRequestObject": {
        "triggerId": data_value,
        "ipAddresses": [],
        "opCode": 101,
        "loadImageDir": "/flash/working",
        "delay": 0,
        "sessionId": None,
        "user": None,
        "deviceMap": {}
    }
}

dico_ap = {}

for i in range(0, count_ap ):
    #print("AP ip & id :",data['response'][i]['ipAddress'],data['response'][i]['instanceid'])
    ip_address = data['response'][i]['ipAddress']  
    instance_id = data['response'][i]['instanceid']
    dico_ap[i] = {"ip": ip_address, "id": instance_id}

for _, values in dico_ap.items():
    ip_address = values["ip"]
    instance_id = values["id"]
    body["TriggerConfigDeviceOperationsRequestObject"]["deviceMap"][instance_id] = ip_address


response = requests.post(url4, headers=headers2, json=body, verify=False) # Envoi d'un Save to Running vers toutes les APS
data = response.json()
print(data)



