import requests
import json

from MHRS.MhrsUser import MhrsUserRoot
from MHRS.Appointment.MhrsObject import MhrsObject

from Database.LocalDatabase import LocalDatabase

class Mhrs():
    def __init__(self):
        self.localDatabase = LocalDatabase()


    def check_login_token_validity(self, token):

        if len(token) == 0:
            token = "-1"

        headers = {
            'Accept': 'application/json, text/plain, */*',
            'Accept-Language': 'en-US',
            'Access-Control-Allow-Credentials': 'true',
            'Access-Control-Allow-Headers': 'Authorization,Content-Type, Accept, X-Requested-With, remember-me',
            'Access-Control-Allow-Methods': 'DELETE, POST, GET, OPTIONS',
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Max-Age': '3600',
            'Authorization': f'Bearer {token}',
            'Cache-Control': 'no-cache',
            'Connection': 'keep-alive',
            'Origin': 'https://mhrs.gov.tr',
            'Pragma': 'no-cache',
            'Referer': 'https://mhrs.gov.tr/',
            'Sec-Fetch-Dest': 'empty',
            'Sec-Fetch-Mode': 'cors',
            'Sec-Fetch-Site': 'same-site',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36',
            'sec-ch-ua': '"Chromium";v="130", "Google Chrome";v="130", "Not?A_Brand";v="99"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"Windows"',
        }

        try:
            response = requests.get('https://prd.mhrs.gov.tr/api/vatandas/vatandas/hasta-bilgisi', headers=headers)
            if response.status_code == 200:
                return True
            
        except requests.exceptions.Timeout:
            print("timeout - check_login_token_validity")

        return False
    
    def login(self, tcno, mhrsPassword, checkValidity=False, token=""):

        resultString = '{ "success":"", "token": "", "new": "" }'
        resultJson = json.loads(resultString)

        if checkValidity == True:
            checkLoginTokenValidity = self.check_login_token_validity(token=token)

            if checkLoginTokenValidity == True:
                resultJson["success"] = True
                resultJson["token"] = token
                resultJson["new"] = False
                return resultJson

        headers = {
            'Accept': 'application/json, text/plain, */*',
            'Accept-Language': 'en-US',
            'Access-Control-Allow-Credentials': 'true',
            'Access-Control-Allow-Headers': 'Authorization,Content-Type, Accept, X-Requested-With, remember-me',
            'Access-Control-Allow-Methods': 'DELETE, POST, GET, OPTIONS',
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Max-Age': '3600',
            'Cache-Control': 'no-cache',
            'Connection': 'keep-alive',
            'Content-Type': 'application/json',
            'Origin': 'https://mhrs.gov.tr',
            'Pragma': 'no-cache',
            'Referer': 'https://mhrs.gov.tr/',
            'Sec-Fetch-Dest': 'empty',
            'Sec-Fetch-Mode': 'cors',
            'Sec-Fetch-Site': 'same-site',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36',
            'sec-ch-ua': '"Chromium";v="130", "Google Chrome";v="130", "Not?A_Brand";v="99"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"Windows"',
        }

        json_data = {
            'kullaniciAdi': tcno,
            'parola': mhrsPassword,
            'islemKanali': 'VATANDAS_RESPONSIVE',
            'girisTipi': 'PAROLA',
            'captchaKey': None,
        }

        try:
            response = requests.post('https://prd.mhrs.gov.tr/api/vatandas/login', headers=headers, json=json_data)

            responseJson = json.loads(response.text)

            if len(responseJson["errors"]) > 0:
                resultJson["success"] = False
            else:
                resultJson["success"] = True
                resultJson["token"] = responseJson["data"]["jwt"]
                resultJson["new"] = True

        except requests.exceptions.Timeout:
            print("timeout - login")
            resultJson["success"] = False
        except requests.exceptions.ConnectionError:
            None
        
        return resultJson
            
    def get_mhrs_users_from_file(self):
        mhrsUsers = None

        try:
            mhrsUsers = self.localDatabase.get_users()
        except Exception as ex:
            None

        return mhrsUsers

    def get_mhrs_cities(self, token):
        cityResponse = []

        headers = {
            'Accept': 'application/json, text/plain, */*',
            'Accept-Language': 'tr-TR',
            'Access-Control-Allow-Credentials': 'true',
            'Access-Control-Allow-Headers': 'Authorization,Content-Type, Accept, X-Requested-With, remember-me',
            'Access-Control-Allow-Methods': 'DELETE, POST, GET, OPTIONS',
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Max-Age': '3600',
            'Authorization': f'Bearer {token}',
            'Cache-Control': 'no-cache',
            'Connection': 'keep-alive',
            'Origin': 'https://mhrs.gov.tr',
            'Pragma': 'no-cache',
            'Referer': 'https://mhrs.gov.tr/',
            'Sec-Fetch-Dest': 'empty',
            'Sec-Fetch-Mode': 'cors',
            'Sec-Fetch-Site': 'same-site',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36',
            'sec-ch-ua': '"Chromium";v="130", "Google Chrome";v="130", "Not?A_Brand";v="99"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"Windows"',
        }

        try:
            response = requests.get('https://prd.mhrs.gov.tr/api/yonetim/genel/il/selectinput-tree', headers=headers)

            if response.status_code == 200:
                
                responseJson = response.json()

                for city in responseJson:
                    cityRow = MhrsObject.City(city["value"], city["text"])
                    cityResponse.append(cityRow)

                    for cityChildren in city["children"]:
                        cityRow = MhrsObject.City(cityChildren["value"], cityChildren["text"])
                        cityResponse.append(cityRow)
            else:
                None
        except requests.exceptions.Timeout:
            print("timeout - get_mhrs_cities")
        except requests.exceptions.ConnectionError:
            None

        return cityResponse

    def get_mhrs_districts(self, token, cityCode):
        districtsResponse = []

        headers = {
            'Accept': 'application/json, text/plain, */*',
            'Accept-Language': 'tr-TR',
            'Access-Control-Allow-Credentials': 'true',
            'Access-Control-Allow-Headers': 'Authorization,Content-Type, Accept, X-Requested-With, remember-me',
            'Access-Control-Allow-Methods': 'DELETE, POST, GET, OPTIONS',
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Max-Age': '3600',
            'Authorization': f'Bearer {token}',
            'Cache-Control': 'no-cache',
            'Connection': 'keep-alive',
            'Origin': 'https://mhrs.gov.tr',
            'Pragma': 'no-cache',
            'Referer': 'https://mhrs.gov.tr/',
            'Sec-Fetch-Dest': 'empty',
            'Sec-Fetch-Mode': 'cors',
            'Sec-Fetch-Site': 'same-site',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36',
            'sec-ch-ua': '"Chromium";v="130", "Google Chrome";v="130", "Not?A_Brand";v="99"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"Windows"',
        }

        try:
            response = requests.get(f'https://prd.mhrs.gov.tr/api/yonetim/genel/ilce/selectinput/{cityCode}', headers=headers)

            if response.status_code == 200:
                
                responseJson = response.json()

                for district in responseJson:
                    districtRow = MhrsObject.District(district["value"], district["text"])
                    districtsResponse.append(districtRow)

            else:
                None
        except requests.exceptions.Timeout:
            print("timeout - get_mhrs_districts")
        except requests.exceptions.ConnectionError:
            None

        return districtsResponse

    def get_mhrs_clinicals(self, token, cityCode, districtCode):
        clinicalsResponse = []

        headers = {
            'Accept': 'application/json, text/plain, */*',
            'Accept-Language': 'tr-TR',
            'Access-Control-Allow-Credentials': 'true',
            'Access-Control-Allow-Headers': 'Authorization,Content-Type, Accept, X-Requested-With, remember-me',
            'Access-Control-Allow-Methods': 'DELETE, POST, GET, OPTIONS',
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Max-Age': '3600',
            'Authorization': f'Bearer {token}',
            'Cache-Control': 'no-cache',
            'Connection': 'keep-alive',
            'Origin': 'https://mhrs.gov.tr',
            'Pragma': 'no-cache',
            'Referer': 'https://mhrs.gov.tr/',
            'Sec-Fetch-Dest': 'empty',
            'Sec-Fetch-Mode': 'cors',
            'Sec-Fetch-Site': 'same-site',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36',
            'sec-ch-ua': '"Chromium";v="130", "Google Chrome";v="130", "Not?A_Brand";v="99"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"Windows"',
        }

        try:
            response = requests.get(f'https://prd.mhrs.gov.tr/api/kurum/kurum/kurum-klinik/il/{cityCode}/ilce/{districtCode}/kurum/-1/aksiyon/200/select-input', headers=headers)

            if response.status_code == 200:
                
                responseJson = response.json()

                for clinical in responseJson["data"]:
                    clinicalRow = MhrsObject.Clinical(clinical["value"], clinical["text"])
                    clinicalsResponse.append(clinicalRow)

            else:
                None
        except requests.exceptions.Timeout:
            print("timeout - get_mhrs_clinicals")
        except requests.exceptions.ConnectionError:
            None

        return clinicalsResponse

    def get_mhrs_hospitals(self, token, cityCode, districtCode, clinicalCode):
        hospitalsResponse = []

        headers = {
            'Accept': 'application/json, text/plain, */*',
            'Accept-Language': 'tr-TR',
            'Access-Control-Allow-Credentials': 'true',
            'Access-Control-Allow-Headers': 'Authorization,Content-Type, Accept, X-Requested-With, remember-me',
            'Access-Control-Allow-Methods': 'DELETE, POST, GET, OPTIONS',
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Max-Age': '3600',
            'Authorization': f'Bearer {token}',
            'Cache-Control': 'no-cache',
            'Connection': 'keep-alive',
            'Origin': 'https://mhrs.gov.tr',
            'Pragma': 'no-cache',
            'Referer': 'https://mhrs.gov.tr/',
            'Sec-Fetch-Dest': 'empty',
            'Sec-Fetch-Mode': 'cors',
            'Sec-Fetch-Site': 'same-site',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36',
            'sec-ch-ua': '"Chromium";v="130", "Google Chrome";v="130", "Not?A_Brand";v="99"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"Windows"',
        }
        
        try:
            response = requests.get(f'https://prd.mhrs.gov.tr/api/kurum/kurum/kurum-klinik/il/{cityCode}/ilce/{districtCode}/kurum/-1/klinik/{clinicalCode}/ana-kurum/select-input', headers=headers)

            if response.status_code == 200:
                
                responseJson = response.json()

                for hospital in responseJson["data"]:
                    try:
                        index = [ x.hospitalCode for x in hospitalsResponse ].index(hospital["value"])
                    except Exception as ex:
                        index = -1

                    if index == -1:
                        hospitalRow = MhrsObject.Hospital(hospital["value"], hospital["text"])
                        hospitalsResponse.append(hospitalRow)

            else:
                None
        except requests.exceptions.Timeout:
            print("timeout - get_mhrs_hospitals")
        except requests.exceptions.ConnectionError:
            None

        return hospitalsResponse

    def get_mhrs_doctors(self, token, hospitalCode, clinicalCode):
        doctorsResponse = []

        headers = {
            'Accept': 'application/json, text/plain, */*',
            'Accept-Language': 'tr-TR',
            'Access-Control-Allow-Credentials': 'true',
            'Access-Control-Allow-Headers': 'Authorization,Content-Type, Accept, X-Requested-With, remember-me',
            'Access-Control-Allow-Methods': 'DELETE, POST, GET, OPTIONS',
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Max-Age': '3600',
            'Authorization': f'Bearer {token}',
            'Cache-Control': 'no-cache',
            'Connection': 'keep-alive',
            'Origin': 'https://mhrs.gov.tr',
            'Pragma': 'no-cache',
            'Referer': 'https://mhrs.gov.tr/',
            'Sec-Fetch-Dest': 'empty',
            'Sec-Fetch-Mode': 'cors',
            'Sec-Fetch-Site': 'same-site',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36',
            'sec-ch-ua': '"Chromium";v="130", "Google Chrome";v="130", "Not?A_Brand";v="99"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"Windows"',
        }

        try:
            response = requests.get(f'https://prd.mhrs.gov.tr/api/kurum/hekim/hekim-klinik/hekim-select-input/anakurum/{hospitalCode}/kurum/-1/klinik/{clinicalCode}', headers=headers)

            if response.status_code == 200:
                
                responseJson = response.json()

                for doctor in responseJson["data"]:
                    doctorRow = MhrsObject.Doctor(doctor["value"], doctor["text"])
                    doctorsResponse.append(doctorRow)

            else:
                None
        except requests.exceptions.Timeout:
            print("timeout - get_mhrs_doctors")
        except requests.exceptions.ConnectionError:
            None

        return doctorsResponse

    def check_available_appointments(self, token, cityCode, districtCode, clinicalCode, hospitalCode, doctorCode):
        appointmentsResponse = []

        headers = {
            'Accept': 'application/json, text/plain, */*',
            'Accept-Language': 'tr-TR',
            'Access-Control-Allow-Credentials': 'true',
            'Access-Control-Allow-Headers': 'Authorization,Content-Type, Accept, X-Requested-With, remember-me',
            'Access-Control-Allow-Methods': 'DELETE, POST, GET, OPTIONS',
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Max-Age': '3600',
            'Authorization': f'Bearer {token}',
            'Cache-Control': 'no-cache',
            'Connection': 'keep-alive',
            'Content-Type': 'application/json',
            'Origin': 'https://mhrs.gov.tr',
            'Pragma': 'no-cache',
            'Referer': 'https://mhrs.gov.tr/',
            'Sec-Fetch-Dest': 'empty',
            'Sec-Fetch-Mode': 'cors',
            'Sec-Fetch-Site': 'same-site',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36',
            'sec-ch-ua': '"Chromium";v="130", "Google Chrome";v="130", "Not?A_Brand";v="99"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"Windows"',
        }

        mhrsCityCode = int(cityCode) if cityCode != "" else -1
        mhrsDistrictCode = int(districtCode) if districtCode != "" else -1
        mhrsClinicalCode = int(clinicalCode) if clinicalCode != "" else -1
        mhrsHospitalCode = int(hospitalCode) if hospitalCode != "" else -1
        mhrsDoctorCode = int(doctorCode) if doctorCode != "" else -1

        json_data = {
            'aksiyonId': '200',
            'cinsiyet': 'F',
            'mhrsHekimId': mhrsDoctorCode,
            'mhrsIlId': mhrsCityCode,
            'mhrsIlceId': mhrsDistrictCode,
            'mhrsKlinikId': mhrsClinicalCode,
            'mhrsKurumId': mhrsHospitalCode,
            'muayeneYeriId': -1,
            'tumRandevular': True,
            'ekRandevu': True,
            'randevuZamaniList': [],
        }

        try:
            response = requests.post('https://prd.mhrs.gov.tr/api/kurum-rss/randevu/slot-sorgulama/arama', headers=headers, json=json_data)

            if response.status_code == 200:
                responseJson = response.json()

                for appointment in responseJson["data"]["hastane"]:
                    doctorName = ""
                    doctorCode = ""

                    try:
                        doctorCode = appointment["hekim"]["mhrsHekimId"]
                        doctorName = appointment["hekim"]["ad"] + " " + appointment["hekim"]["soyad"]
                    except Exception as ex:
                        None

                    appointmentRow = MhrsObject.Appointment(cityCode=appointment["kurum"]["ilIlce"]["mhrsIlId"],
                                                            cityName=appointment["kurum"]["ilIlce"]["ilAdi"],
                                                            districtCode=appointment["kurum"]["ilIlce"]["mhrsIlceId"],
                                                            districtName=appointment["kurum"]["ilIlce"]["ilceAdi"],
                                                            hospitalCode=appointment["kurum"]["mhrsKurumId"],
                                                            hospitalName=appointment["kurum"]["kurumKisaAdi"],
                                                            clinicalCode=appointment["klinik"]["mhrsKlinikId"],
                                                            clinicalName=appointment["klinik"]["mhrsKlinikAdi"],
                                                            doctorCode=doctorCode,
                                                            doctorName=doctorName,
                                                            isAvailable=appointment["bos"], 
                                                            availableCount=appointment["bosKapasite"],
                                                            earliestDay=appointment["baslangicZamaniStr"]["tarih"],
                                                            earliestDayText=appointment["baslangicZamaniStr"]["gunAyGunIsmi"])
                    appointmentsResponse.append(appointmentRow)
            else:
                None
        except requests.exceptions.Timeout:
            print("timeout - check_available_appointments")
        except requests.exceptions.ConnectionError:
            None
     
        return appointmentsResponse
    
    def make_an_appointment(self, mhrsToken, appointmentInfo:MhrsObject.Appointment):
        responseText = '{"success": "", "hospitalName": "", "doctorName": "", "appointmentDate": "", "appointmentTime": ""}'
        responseObject = json.loads(responseText)

        headers = {
            'Accept': 'application/json, text/plain, */*',
            'Accept-Language': 'tr-TR',
            'Access-Control-Allow-Credentials': 'true',
            'Access-Control-Allow-Headers': 'Authorization,Content-Type, Accept, X-Requested-With, remember-me',
            'Access-Control-Allow-Methods': 'DELETE, POST, GET, OPTIONS',
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Max-Age': '3600',
            'Authorization': f'Bearer {mhrsToken}',
            'Cache-Control': 'no-cache',
            'Connection': 'keep-alive',
            'Content-Type': 'application/json',
            'Origin': 'https://mhrs.gov.tr',
            'Pragma': 'no-cache',
            'Referer': 'https://mhrs.gov.tr/',
            'Sec-Fetch-Dest': 'empty',
            'Sec-Fetch-Mode': 'cors',
            'Sec-Fetch-Site': 'same-site',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36',
            'sec-ch-ua': '"Chromium";v="130", "Google Chrome";v="130", "Not?A_Brand";v="99"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"Windows"',
        }
        
        slots = self.get_appointment_slots(mhrsToken=mhrsToken, appointmentInfo=appointmentInfo)

        if slots != None:
            for data in slots["data"]:
                for doctorSlot in data["hekimSlotList"]:
                    for examinaitonPlace in doctorSlot["muayeneYeriSlotList"]:
                        for hourSlot in examinaitonPlace["saatSlotList"]:
                            for slot in hourSlot["slotList"]:
                                
                                if slot["bos"] == True:

                                    #Randevu al
                                    json_data = {
                                        'fkSlotId': slot["id"],
                                        'fkCetvelId': slot["fkCetvelId"],
                                        'yenidogan': False,
                                        'muayeneYeriId': slot["slot"]["muayeneYeriId"],
                                        'baslangicZamani': slot["baslangicZamani"],
                                        'bitisZamani': slot["bitisZamani"],
                                        'randevuNotu': '',
                                    }

                                    try:
                                        response = requests.post('https://prd.mhrs.gov.tr/api/kurum/randevu/randevu-ekle', headers=headers, json=json_data)

                                        if response.status_code == 200:
                                            responseObject["success"] = True
                                            responseObject["hospitalName"] = doctorSlot["kurum"]["kurumAdi"]
                                            responseObject["doctorName"] = doctorSlot["hekim"]["ad"] + " " + doctorSlot["hekim"]["soyad"]
                                            responseObject["appointmentDate"] = slot["baslangicZamanStr"]["gunAyGunIsmi"]
                                            responseObject["appointmentTime"] = slot["baslangicZamanStr"]["saat"]
                                            return responseObject
                                    except requests.exceptions.Timeout:
                                        print("timeout - make_an_appointment")
                                        responseObject["success"] = False
                                        return responseObject
                                    except requests.exceptions.ConnectionError:
                                        responseObject["success"] = False
                                        return responseObject
        
        responseObject["success"] = False
        return responseObject

    def get_appointment_slots(self, mhrsToken, appointmentInfo:MhrsObject.Appointment):
        headers = {
            'Accept': 'application/json, text/plain, */*',
            'Accept-Language': 'tr-TR',
            'Access-Control-Allow-Credentials': 'true',
            'Access-Control-Allow-Headers': 'Authorization,Content-Type, Accept, X-Requested-With, remember-me',
            'Access-Control-Allow-Methods': 'DELETE, POST, GET, OPTIONS',
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Max-Age': '3600',
            'Authorization': f'Bearer {mhrsToken}',
            'Cache-Control': 'no-cache',
            'Connection': 'keep-alive',
            'Content-Type': 'application/json',
            'Origin': 'https://mhrs.gov.tr',
            'Pragma': 'no-cache',
            'Referer': 'https://mhrs.gov.tr/',
            'Sec-Fetch-Dest': 'empty',
            'Sec-Fetch-Mode': 'cors',
            'Sec-Fetch-Site': 'same-site',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36',
            'sec-ch-ua': '"Chromium";v="130", "Google Chrome";v="130", "Not?A_Brand";v="99"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"Windows"',
        }

        json_data = {
            'aksiyonId': 200,
            'mhrsHekimId': int(appointmentInfo.doctorCode),
            'mhrsIlId': int(appointmentInfo.cityCode),
            'mhrsKlinikId': int(appointmentInfo.clinicalCode),
            'mhrsKurumId': int(appointmentInfo.hospitalCode),
            'muayeneYeriId': -1,
            'cinsiyet': 'F',
            'tumRandevular': False,
            'ekRandevu': True,
            'randevuZamaniList': [],
        }

        try:
            response = requests.post('https://prd.mhrs.gov.tr/api/kurum-rss/randevu/slot-sorgulama/slot', headers=headers, json=json_data)

            responseJson = response.json()
            return responseJson
        except requests.exceptions.Timeout:
            print("timeout - get_appointment_slots")
        except requests.exceptions.ConnectionError:
            None