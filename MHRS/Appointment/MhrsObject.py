class MhrsObject():

    class City():
        def __init__(self, cityCode, cityName):
            self.cityCode = cityCode
            self.cityName = cityName
            
    class District():
        def __init__(self, districtCode, districtName):
            self.districtCode = districtCode
            self.districtName = districtName

    class Clinical():
        def __init__(self, clinicalCode, clinicalName):
            self.clinicalCode = clinicalCode
            self.clinicalName = clinicalName

    class Hospital():
        def __init__(self, hospitalCode, hospitalName):
            self.hospitalCode = hospitalCode
            self.hospitalName = hospitalName
    
    class Doctor():
        def __init__(self, doctorCode, doctorName):
            self.doctorCode = doctorCode
            self.doctorName = doctorName

    class Appointment():
        def __init__(self, userId="", appointmentId="", cityCode="", cityName="", districtCode="", districtName="", hospitalCode="", hospitalName="", clinicalCode="", clinicalName="", doctorCode="", doctorName="", isAvailable="", availableCount="", earliestDay="", earliestDayText="", makeAnAppointment=""):
            self.userId = userId
            self.appointmentId = appointmentId
            self.cityCode = cityCode
            self.cityName = cityName
            self.districtCode = districtCode
            self.districtName = districtName 
            self.clinicalCode = clinicalCode
            self.clinicalName = clinicalName
            self.hospitalCode = hospitalCode
            self.hospitalName = hospitalName
            self.doctorCode = doctorCode
            self.doctorName = doctorName
            self.isAvailable = isAvailable
            self.availableCount = availableCount
            self.earliestDay = earliestDay
            self.earliestDayText = earliestDayText
            self.makeAnAppointment = makeAnAppointment
