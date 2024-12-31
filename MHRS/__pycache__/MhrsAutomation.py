import requests
import json
import datetime
import os
import time
import nest_asyncio
import asyncio
import sys
from threading import Thread, Barrier
from Telegram.Telegram import Telegram

from MHRS.Mhrs import Mhrs
from MHRS.Appointment.MhrsObject import MhrsObject
from Database.LocalDatabase import LocalDatabase

nest_asyncio.apply()

if sys.platform:
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

class MhrsAutomation:

    def __init__(self, telegram=None):
        self.telegram = telegram

    def check_login_token_validity(self, token):
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

        response = requests.get('https://prd.mhrs.gov.tr/api/vatandas/vatandas/hasta-bilgisi', headers=headers)

        if response.status_code == 200:
            return True
        else:
            return False

    def login(self, username, password):
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
            'kullaniciAdi': username,
            'parola': password,
            'islemKanali': 'VATANDAS_RESPONSIVE',
            'girisTipi': 'PAROLA',
            'captchaKey': None,
        }

        response = requests.post('https://prd.mhrs.gov.tr/api/vatandas/login', headers=headers, json=json_data)

        responseJson = json.loads(response.text)

        if len(responseJson["errors"]) > 0:
            input("Giriş yapılırken hata meydana geldi!")
            return -1
        
        return responseJson["data"]["jwt"]

    def check_family_doctor_available(self, token, mhrsDoctorId, mhrsInstitutionId):
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

        json_data = {
            'aksiyonId': '100',
            'mhrsHekimId': mhrsDoctorId,
            'mhrsKurumId': mhrsInstitutionId,
        }

        response = requests.post('https://prd.mhrs.gov.tr/api/kurum-rss/randevu/slot-sorgulama/slot', headers=headers, json=json_data)

        if response.status_code != 404:
            return True
        else:
            return False

    def get_mhrs_users_from_file(self):
        mhrsUsers = []

        try:
            with open("MhrsUsers.json", "r") as jsonFile:
                mhrsUsers = json.load(jsonFile)
        except Exception as ex:
            None

        return mhrsUsers

    async def start(self):
        mhrsUsers = self.get_mhrs_users_from_file()
        foundUsers = []

        localDatabase = LocalDatabase()
        mhrs = Mhrs()

        while True:
            await asyncio.sleep(1)

            os.system('cls')

            now = datetime.datetime.now()
            hourTxt = now.hour if len(str(now.hour)) == 2 else f"0{str(now.hour)}"
            minuteTxt = now.minute if len(str(now.minute)) == 2 else f"0{str(now.minute)}"
            secondTxt = now.second if len(str(now.second)) == 2 else f"0{str(now.second)}"

            
            print(str(hourTxt) + ":" + str(minuteTxt) + ":" + str(secondTxt) + "\n")

            mhrsUsers = mhrs.get_mhrs_users_from_file()
            appointments = localDatabase.get_all_appointments()

            for appointment in appointments:
                try:
                    mhrsUserIndex = [ str(x.userId) for x in mhrsUsers ].index(str(appointment.userId))
                except Exception as ex:
                    mhrsUserIndex = -1

                if mhrsUserIndex >= 0:
                    mhrsUser = mhrsUsers[mhrsUserIndex]

                    #Login kontrol
                    loginResult = mhrs.login(tcno=mhrsUser.tcno,
                                             mhrsPassword=mhrsUser.password,
                                             checkValidity=True,
                                             token=mhrsUser.mhrsToken)
                        
                    if loginResult["success"] == True:
                        mhrsUsers[mhrsUserIndex].mhrsToken = loginResult["token"]
                        mhrsUser.mhrsToken = loginResult["token"]

                        if loginResult["new"] == True:
                            localDatabase.update_mhrs_token(userId=mhrsUser.userId,
                                                            mhrsToken=mhrsUser.mhrsToken)


                    #Uygun randevu
                    availableAppointments = mhrs.check_available_appointments(token=mhrsUser.mhrsToken, 
                                                                              cityCode=appointment.cityCode,
                                                                              districtCode=appointment.districtCode,
                                                                              clinicalCode=appointment.clinicalCode,
                                                                              hospitalCode=appointment.hospitalCode,
                                                                              doctorCode=appointment.doctorCode)
                    
                    if len(availableAppointments) > 0:

                        messageContent = "Takip listenizde olan randevular için uygunluk bulunmuştur:\n\n"

                        for availableAppointment in availableAppointments:
                            if appointment.makeAnAppointment == "0":
                                messageContent += f"<b>İl/İlçe</b> : {availableAppointment.cityName}/{availableAppointment.districtName}\n"
                                messageContent += f"<b>Klinik</b> : {availableAppointment.clinicalName}\n"
                                messageContent += f"<b>Hastane</b> : {availableAppointment.hospitalName}\n"
                                messageContent += f"<b>Doktor</b> : {availableAppointment.doctorName}\n"
                                messageContent += f"<b>Uygun Tarih</b> : {availableAppointment.earliestDayText}\n"
                                messageContent += "\n"
                            else:
                                #Randevu al seçiliyse
                                appointmentInfo = MhrsObject.Appointment()
                                appointmentInfo.cityCode = availableAppointment.cityCode
                                appointmentInfo.clinicalCode = availableAppointment.clinicalCode
                                appointmentInfo.hospitalCode = availableAppointment.hospitalCode
                                appointmentInfo.doctorCode = availableAppointment.doctorCode

                                makeAnAppointmentResult = mhrs.make_an_appointment(mhrsToken=mhrsUser.mhrsToken, appointmentInfo=appointmentInfo)

                                if makeAnAppointmentResult["success"] == True:
                                    messageContent = ""

                                    messageContent += "Takip listenizdeki randevunuz alınmıştır:\n\n"
                                    messageContent += f"<b>İl/İlçe</b> : {appointment.cityName}/{appointment.districtName}\n"
                                    messageContent += f"<b>Klinik</b> : {appointment.clinicalName}\n"
                                    messageContent += f"<b>Hastane</b> : {makeAnAppointmentResult["hospitalName"]}\n"
                                    messageContent += f"<b>Doktor</b> : {makeAnAppointmentResult["doctorName"]}\n"
                                    messageContent += f"<b>Tarih</b> : {makeAnAppointmentResult["appointmentDate"]}\n"
                                    messageContent += f"<b>Saat</b> : {makeAnAppointmentResult["appointmentTime"]}\n"

                                    break

                        #Sistemden randevu kaldırılır
                        localDatabase.delete_appointment(userId=mhrsUser.userId, appointmentId=appointment.appointmentId)


                        if len(messageContent) > 0:
                            entity = await self.telegram.get_entity(int(mhrsUser.telegramId))
                            await self.telegram.send_message(chatId=entity, statusIndex=-1, messageContent=messageContent, noOverrideLastMessageId=True)
            
            print("\n30 saniye beklenecektir")
            await asyncio.sleep(30)
        
    def start_old(self):
        telegram = Telegram(api_id=24406313, api_hash=" 57db945e1f947621360f79a7b7d44f14 ", bot_token="5816521378922:AAHyIKu5Tctd4213IUlDtfAtsViW8q7E979D1Y")
        telegram.login()

        mhrsUsers = self.get_mhrs_users_from_file()
        foundUsers = []

        if len(mhrsUsers) > 0:
            while True:
                os.system('cls')

                now = datetime.datetime.now()
                hourTxt = now.hour if len(str(now.hour)) == 2 else f"0{str(now.hour)}"
                minuteTxt = now.minute if len(str(now.minute)) == 2 else f"0{str(now.minute)}"
                secondTxt = now.second if len(str(now.second)) == 2 else f"0{str(now.second)}"

                
                print(str(hourTxt) + ":" + str(minuteTxt) + ":" + str(secondTxt) + "\n")

                try:
                    for user in mhrsUsers["users"]:
                        if len(user["token"]) > 0:
                            checkLoginTokenResult = self.check_login_token_validity(user["token"])
                        else:
                            checkLoginTokenResult = False

                        if checkLoginTokenResult == False:
                            loginToken = self.login(user["username"], user["password"])

                            if loginToken == -1:
                                input(f"{user["username"]} kullanıcısı ile giriş yapılamadı!")
                                continue
                            else:
                                #Yeni token ile güncellenir
                                user["token"] = loginToken

                                with open("MhrsUsers.json", "w") as jsonFile:
                                    json.dump(mhrsUsers, jsonFile)

                        familyDoctorAvailableResult = self.check_family_doctor_available(user["token"], user["mhrsDoctorId"], user["mhrsInstitutionId"])

                        if familyDoctorAvailableResult == False:
                            if user["username"] in foundUsers:
                                foundUsers.remove(user["username"])

                            print(f"{user["username"]} için geçerli randevu bilgisi bulunamadı!")
                        else:
                            if user["username"] in foundUsers:
                                continue
                            
                            #Uygun randevu varsa
                            foundUsers.append(user["username"])

                            asyncio.run(telegram.send_available_family_doctor(username=user["username"]))
                            
                except Exception as ex:
                    continue

                print("\n1 dk beklenecektir")
                time.sleep(60)
                        
        else:
            input("Kayıtlı MHRS kullanıcısı bulunamadı!")
            return

    async def main(self):
        localDatabase = LocalDatabase()

        self.telegram = Telegram(api_id=26953503, api_hash=" 57db945e1f947621360f79a7b7d44f14 ", bot_token="269535032313:AAFUkZBZDPERN7213OgOSVUZ32WI7V-WII5PY", localDatabase=localDatabase)
        await self.telegram.login()
        #entity = await self.telegram.get_entity("testgroup12247")

        

        await asyncio.gather(
            self.start(),
            self.telegram.listen_messages()
        )

mhrsAutomation = MhrsAutomation()
asyncio.run(mhrsAutomation.main())






