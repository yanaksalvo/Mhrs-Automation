class MhrsUserRoot():
    def __init__(self, users):
        if users != None:
            self.users = [MhrsUser(**user) for user in users]
        else:
            self.users = []

class MhrsUser():
    def __init__(self, userId, tcno, password, telegramId, mhrsToken="", activeAppointments=[]):
        self.userId = userId
        self.tcno = tcno
        self.password = password
        self.telegramId = telegramId
        self.mhrsToken = mhrsToken
        self.activeAppointments = [Appointments(**appointment) for appointment in activeAppointments]

class Appointments():
    def __init__(self, cityCode, districtCode, clinicalCode, hospitalCode, doctorCode):
        self.cityCode = cityCode
        self.districtCode = districtCode
        self.clinicalCode = clinicalCode
        self.hospitalCode = hospitalCode
        self.doctorCode = doctorCode