from flask import Flask, request
from flask_restful import Resource, Api, abort, reqparse
from flask_cors import CORS
import werkzeug
from firebase import Firebase

app = Flask(__name__)
api = Api(app)
CORS(app)

config = {
  "apiKey": "AIzaSyCwpZAGJgBRdYpuYxD7OhhJr991uQcEEKc",
  "authDomain": "database-9c6e7.firebaseapp.com",
  "databaseURL": "https://database-9c6e7-default-rtdb.firebaseio.com",
  "storageBucket": "database-9c6e7.appspot.com"
}

config_admin = {
  "apiKey": "AIzaSyCwpZAGJgBRdYpuYxD7OhhJr991uQcEEKc",
  "authDomain": "database-9c6e7.firebaseapp.com",
  "databaseURL": "https://database-9c6e7-default-rtdb.firebaseio.com",
  "storageBucket": "database-9c6e7.appspot.com"
}

firebase=Firebase(config)
db=firebase.database()
storage = firebase.storage()

firebase_admin=Firebase(config)
db_admin=firebase_admin.database()

childName = 'AutomaticTimeTable'

loginParser=reqparse.RequestParser()
loginParser.add_argument('cat', type=str, required=True)
loginParser.add_argument('username', type=str, required=True)
loginParser.add_argument('password', type=str, required=True)

departmentRegParser=reqparse.RequestParser()
departmentRegParser.add_argument('name', type=str, required=True)
departmentRegParser.add_argument('semCount', type=int, required=True)

departmentUpdateParser=reqparse.RequestParser()
departmentUpdateParser.add_argument('name', type=str)
departmentUpdateParser.add_argument('semCount', type=int)

subjectRegParser=reqparse.RequestParser()
subjectRegParser.add_argument('name', type=str, required=True)
subjectRegParser.add_argument('deptID', type=str, required=True)
subjectRegParser.add_argument('sem', type=int, required=True)
subjectRegParser.add_argument('hours', type=int, required=True)

subjectUpdateParser=reqparse.RequestParser()
subjectUpdateParser.add_argument('name', type=str)
subjectUpdateParser.add_argument('hours', type=int)

lectureRegParser=reqparse.RequestParser()
lectureRegParser.add_argument('name', type=str, required=True)
lectureRegParser.add_argument('deptID', type=str, required=True)
lectureRegParser.add_argument('designation', type=str, required=True)
lectureRegParser.add_argument('gender', type=str, required=True)
lectureRegParser.add_argument('dob', type=str, required=True)
lectureRegParser.add_argument('email', type=str, required=True)
lectureRegParser.add_argument('mobileNumber', type=int, required=True)
lectureRegParser.add_argument('address', type=str, required=True)
lectureRegParser.add_argument('mon', type=str, required=True, choices=('yes','no'))
lectureRegParser.add_argument('tue', type=str, required=True, choices=('yes','no'))
lectureRegParser.add_argument('wed', type=str, required=True, choices=('yes','no'))
lectureRegParser.add_argument('thu', type=str, required=True, choices=('yes','no'))
lectureRegParser.add_argument('fri', type=str, required=True, choices=('yes','no'))
lectureRegParser.add_argument('photo', type=werkzeug.datastructures.FileStorage, location='files', required=True)

lectureUpdateParser=reqparse.RequestParser()
lectureUpdateParser.add_argument('name', type=str)
lectureUpdateParser.add_argument('designation', type=str)
lectureUpdateParser.add_argument('gender', type=str)
lectureUpdateParser.add_argument('dob', type=str)
lectureUpdateParser.add_argument('email', type=str)
lectureUpdateParser.add_argument('mobileNumber', type=int)
lectureUpdateParser.add_argument('address', type=str)
lectureUpdateParser.add_argument('mon', type=str, choices=('yes','no'))
lectureUpdateParser.add_argument('tue', type=str, choices=('yes','no'))
lectureUpdateParser.add_argument('wed', type=str, choices=('yes','no'))
lectureUpdateParser.add_argument('thu', type=str, choices=('yes','no'))
lectureUpdateParser.add_argument('fri', type=str, choices=('yes','no'))
lectureUpdateParser.add_argument('photo', type=werkzeug.datastructures.FileStorage, location='files')

generateTimeTableParser=reqparse.RequestParser()
generateTimeTableParser.add_argument('semList', type=str, required=True)


feedbackParser = reqparse.RequestParser()
feedbackParser.add_argument('feedback', type=str , required=True)
feedbackParser.add_argument('name' , type=str, required=True)
feedbackParser.add_argument('details' , type=str, required=True)

class Login(Resource):
  def post(self):
      args=loginParser.parse_args()
      adminUsername = db_admin.child(childName).child('adminUsername').get().val()
      if adminUsername == None:
          adminUsername = 'admin@gmail.com'
          db_admin.child(childName).child('adminUsername').set(adminUsername)
      adminPassword = db_admin.child(childName).child('adminPassword').get().val()
      if adminPassword == None:
          adminPassword = 'admin123'
          db_admin.child(childName).child('adminPassword').set(adminPassword)
      lectureList = db.child(childName).child('lectureList').get().val()
      if lectureList == None:
          lectureList = {}
      if args['cat'] == 'admin':
        if args['username'] == adminUsername and args['password'] == adminPassword:
            loginID = 'admin'
        else:
            loginID = 'invalid'
      elif args['cat'] == 'lecture':
        loginID = 'invalid'
        for i in lectureList:
          if lectureList[i]['email'] == args['username'] and str(lectureList[i]['mobileNumber']) == args['password']:
            loginID = i
      return loginID

class DepartmentReg(Resource):
  def post(self):
    args=departmentRegParser.parse_args()
    departmentList = db.child(childName).child('departmentList').get().val()
    if departmentList == None:
        departmentList = {}
    for i in departmentList:
      if departmentList[i]['name'].lower() == args['name'].lower():
        abort(400, message='department already registered')
    if args['semCount'] <= 0:
      abort(400, message='semester count should be greater than 0')
    deptCnt = db.child(childName).child('deptCnt').get().val()
    if deptCnt == None:
        deptCnt = 0
    deptCnt += 1
    deptID = 'DEPT' + str(deptCnt + 100)
    db.child(childName).child('deptCnt').set(deptCnt)
    departmentList[deptID] = args
    db.child(childName).child('departmentList').set(departmentList)
    return departmentList

  def get(self):
    departmentList = db.child(childName).child('departmentList').get().val()
    if departmentList == None:
        departmentList = {}
    return departmentList

class DepartmentUpdate(Resource):
  def put(self, deptID):
    args=departmentUpdateParser.parse_args()
    departmentList = db.child(childName).child('departmentList').get().val()
    if departmentList == None:
        departmentList = {}
    if not deptID in departmentList:
      abort(400, message='department not found')
    if args['name']:
      for i in departmentList:
        if i != deptID and departmentList[i]['name'].lower() == args['name'].lower():
          abort(400, message='department name already used')
      departmentList[deptID]['name'] = args['name']
    if args['semCount']:
      if args['semCount'] <= 0:
        abort(400, message='semester count should be greater than 0')
      departmentList[deptID]['semCount'] = args['semCount']
    db.child(childName).child('departmentList').set(departmentList)
    return departmentList[deptID]

  def delete(self, deptID):
    departmentList = db.child(childName).child('departmentList').get().val()
    if departmentList == None:
        departmentList = {}
    subjectList = db.child(childName).child('subjectList').get().val()
    if subjectList == None:
        subjectList = {}
    if not deptID in departmentList:
      abort(400, message='department not found')
    flag = 0
    for i in subjectList:
      if subjectList[i]['deptID'] == deptID:
        flag = 1
        break
    if flag == 1:
      abort(400, message='department cant be deleted')
    elif flag == 0:
      del departmentList[deptID]
      db.child(childName).child('departmentList').set(departmentList)
    return departmentList

class SubjectReg(Resource):
  def post(self):
    args=subjectRegParser.parse_args()
    departmentList = db.child(childName).child('departmentList').get().val()
    if departmentList == None:
        departmentList = {}
    subjectList = db.child(childName).child('subjectList').get().val()
    if subjectList == None:
        subjectList = {}
    if not args['deptID'] in departmentList:
      abort(400, message='department not found')
    for i in subjectList:
      if subjectList[i]['deptID'] == args['deptID'] and subjectList[i]['name'].lower() == args['name'].lower():
        abort(400, message='subject already registered')
    if args['sem'] <= 0 or args['sem'] > departmentList[args['deptID']]['semCount']:
      abort(400, message='semester out of range')
    subjectCnt = db.child(childName).child('subjectCnt').get().val()
    if subjectCnt == None:
        subjectCnt = 0
    subjectCnt += 1
    subjectID = 'SUB' + str(subjectCnt + 100)
    db.child(childName).child('subjectCnt').set(subjectCnt)
    subjectList[subjectID] = args
    db.child(childName).child('subjectList').set(subjectList)
    return subjectList

  def get(self):
    subjectList = db.child(childName).child('subjectList').get().val()
    if subjectList == None:
        subjectList = {}
    return subjectList

class SubjectUpdate(Resource):
  def put(self, subjectID):
    args=subjectUpdateParser.parse_args()
    subjectList = db.child(childName).child('subjectList').get().val()
    if subjectList == None:
        subjectList = {}
    if not subjectID in subjectList:
      abort(400, message='subject not found')
    if args['name']:
      for i in subjectList:
        if i != subjectID and subjectList[i]['deptID'] == subjectList[subjectID]['deptID'] and subjectList[i]['name'].lower() == args['name'].lower():
          abort(400, message='subject name already used')
      subjectList[subjectID]['name'] = args['name']
    if args['hours']:
      subjectList[subjectID]['hours'] = args['hours']
    db.child(childName).child('subjectList').set(subjectList)
    return subjectList[subjectID]

  def delete(self, subjectID):
    subjectList = db.child(childName).child('subjectList').get().val()
    if subjectList == None:
        subjectList = {}
    if not subjectID in subjectList:
      abort(400, message='subject not found')
    del subjectList[subjectID]
    db.child(childName).child('subjectList').set(subjectList)
    return subjectList

class SubjectList(Resource):
  def get(self, deptID, sem):
    departmentList = db.child(childName).child('departmentList').get().val()
    if departmentList == None:
        departmentList = {}
    subjectList = db.child(childName).child('subjectList').get().val()
    if subjectList == None:
        subjectList = {}
    if not deptID in departmentList:
      abort(400, message='department not found')
    if int(sem) > departmentList[deptID]['semCount'] or int(sem) <= 0:
      abort(400, message='semester out of range')
    tempSubjectList = {}
    for i in subjectList:
      if subjectList[i]['deptID'] == deptID and subjectList[i]['sem'] == int(sem):
        tempSubjectList[i] = subjectList[i]
    return tempSubjectList

class DepartmentSubjectList(Resource):
  def get(self, deptID):
    departmentList = db.child(childName).child('departmentList').get().val()
    if departmentList == None:
        departmentList = {}
    subjectList = db.child(childName).child('subjectList').get().val()
    if subjectList == None:
        subjectList = {}
    if not deptID in departmentList:
      abort(400, message='department not found')
    tempSubjectList = {}
    for i in subjectList:
      if subjectList[i]['deptID'] == deptID:
        tempSubjectList[i] = subjectList[i]
    return tempSubjectList

class LectureReg(Resource):
  def post(self):
    args=lectureRegParser.parse_args()
    departmentList = db.child(childName).child('departmentList').get().val()
    if departmentList == None:
        departmentList = {}
    if not args['deptID'] in departmentList:
      abort(400, message='department not found')
    lectureList = db.child(childName).child('lectureList').get().val()
    if lectureList == None:
        lectureList = {}
    for i in lectureList:
      if lectureList[i]['email'].lower() == args['email'].lower():
        abort(400, message='email id already used')
    lectureCnt = db.child(childName).child('lectureCnt').get().val()
    if lectureCnt == None:
        lectureCnt = 0
    lectureCnt += 1
    lectureID = 'LECT' + str(lectureCnt + 100)
    fname = lectureID + '.jpg'
    f = args['photo']
    del args['photo']
    storage.child(childName).child('lectureImage').child(fname).put(f)
    args['imgUrl'] = storage.child(childName).child('lectureImage').child(fname).get_url(None)
    db.child(childName).child('lectureCnt').set(lectureCnt)
    lectureList = db.child(childName).child('lectureList').get().val()
    if lectureList == None:
        lectureList = {}
    lectureList[lectureID] = args
    db.child(childName).child('lectureList').set(lectureList)
    return lectureList

  def get(self):
    lectureList = db.child(childName).child('lectureList').get().val()
    if lectureList == None:
        lectureList = {}
    return lectureList

class LectureList(Resource):
  def get(self, deptID):
    departmentList = db.child(childName).child('departmentList').get().val()
    if departmentList == None:
        departmentList = {}
    lectureList = db.child(childName).child('lectureList').get().val()
    if lectureList == None:
        lectureList = {}
    if not deptID in departmentList:
      abort(400, message='department not found')
    tempLectureList = {}
    for i in lectureList:
      if lectureList[i]['deptID'] == deptID:
        tempLectureList[i] = lectureList[i]
    return tempLectureList

class LectureUpdate(Resource):
  def get(self, lectureID):
    lectureList = db.child(childName).child('lectureList').get().val()
    if lectureList == None:
        lectureList = {}
    departmentList = db.child(childName).child('departmentList').get().val()
    if departmentList == None:
        departmentList = {}
    if not lectureID in lectureList:
      abort(400, message='lecture not found')
    lectureDetails = lectureList[lectureID]
    lectureDetails['departmentDetails'] = departmentList[lectureDetails['deptID']]
    return lectureDetails

  def put(self, lectureID):
    args=lectureUpdateParser.parse_args()
    lectureList = db.child(childName).child('lectureList').get().val()
    if lectureList == None:
        lectureList = {}
    if not lectureID in lectureList:
      abort(400, message='lecture not found')
    if args['name']:
      lectureList[lectureID]['name'] = args['name']
    if args['designation']:
      lectureList[lectureID]['designation'] = args['designation']
    if args['gender']:
      lectureList[lectureID]['gender'] = args['gender']
    if args['dob']:
      lectureList[lectureID]['dob'] = args['dob']
    if args['email']:
      lectureList[lectureID]['email'] = args['email']
    if args['mobileNumber']:
      lectureList[lectureID]['mobileNumber'] = args['mobileNumber']
    if args['address']:
      lectureList[lectureID]['address'] = args['address']
    if args['mon']:
      lectureList[lectureID]['mon'] = args['mon']
    if args['tue']:
      lectureList[lectureID]['tue'] = args['tue']
    if args['wed']:
      lectureList[lectureID]['wed'] = args['wed']
    if args['thu']:
      lectureList[lectureID]['thu'] = args['thu']
    if args['fri']:
      lectureList[lectureID]['fri'] = args['fri']
    if args['photo']:
        fname  = lectureID +'.jpg'
        storage.child(childName).child('lectureImage').child(fname).put(args['photo'])
        lectureList[lectureID]['imgUrl']=storage.child(childName).child('lectureImage').child(fname).get_url(None)
    db.child(childName).child('lectureList').set(lectureList)
    return lectureList[lectureID]

  def delete(self, lectureID):
    lectureList = db.child(childName).child('lectureList').get().val()
    if lectureList == None:
        lectureList = {}
    if not lectureID in lectureList:
      abort(400, message='lecture not found')
    del lectureList[lectureID]
    db.child(childName).child('lectureList').set(lectureList)
    return  lectureList

class LectureSubject(Resource):
  def post(self, lectureID, subjectID):
    lectureList = db.child(childName).child('lectureList').get().val()
    if lectureList == None:
        lectureList = {}
    subjectList = db.child(childName).child('subjectList').get().val()
    if subjectList == None:
        subjectList = {}
    if not lectureID in lectureList:
      abort(400, message='lecture not found')
    if not subjectID in subjectList:
      abort(400, message='subject not found')
    lectureSubjectList = db.child(childName).child('lectureSubjectList').get().val()
    if lectureSubjectList == None:
        lectureSubjectList = {}
    flag = 0
    for i in lectureSubjectList:
      if lectureSubjectList[i]['lectureID'] == lectureID and lectureSubjectList[i]['subjectID'] == subjectID:
        flag = 1
        break
    if flag == 1:
      abort(400, message='subject already added to the lecture')
    elif flag == 0:
      lectureSubjectCnt = db.child(childName).child('lectureSubjectCnt').get().val()
    if lectureSubjectCnt == None:
        lectureSubjectCnt = 0
    lectureSubjectCnt += 1
    lectSubID = 'LECTSUB' + str(lectureSubjectCnt + 100)
    db.child(childName).child('lectureSubjectCnt').set(lectureSubjectCnt)
    lectureSubjectList[lectSubID] = { 'lectureID' : lectureID, 'subjectID' : subjectID }
    db.child(childName).child('lectureSubjectList').set(lectureSubjectList)
    return lectureSubjectList

  def get(self, lectureID, subjectID):
    lectureList = db.child(childName).child('lectureList').get().val()
    if lectureList == None:
        lectureList = {}
    subjectList = db.child(childName).child('subjectList').get().val()
    if subjectList == None:
        subjectList = {}
    lectureSubjectList = db.child(childName).child('lectureSubjectList').get().val()
    if lectureSubjectList == None:
        lectureSubjectList = {}
    if subjectID == 'nil':
      if not lectureID in lectureList:
        abort(400, message='lecture not found')
      tempSubjectList = {}
      departmentList = db.child(childName).child('departmentList').get().val()
      if departmentList == None:
          departmentList = {}
      for i in lectureSubjectList:
        if lectureSubjectList[i]['lectureID'] == lectureID:
          if lectureSubjectList[i]['subjectID'] in subjectList:
            tempSubjectList[lectureSubjectList[i]['subjectID']] = subjectList[lectureSubjectList[i]['subjectID']]
      for i in tempSubjectList:
        tempSubjectList[i]['departmentDetails'] = departmentList[tempSubjectList[i]['deptID']]
      return tempSubjectList
    elif lectureID == 'nil':
      if not subjectID in subjectList:
        abort(400, message='subject not found')
      tempLectureList = {}
      for i in lectureSubjectList:
        if lectureSubjectList[i]['subjectID'] == subjectID:
          tempLectureList[lectureSubjectList[i]['lectureID']] = lectureList[lectureSubjectList[i]['lectureID']]
      return tempLectureList

  def delete(self, lectureID, subjectID):
    lectureList = db.child(childName).child('lectureList').get().val()
    if lectureList == None:
        lectureList = {}
    subjectList = db.child(childName).child('subjectList').get().val()
    if subjectList == None:
        subjectList = {}
    lectureSubjectList = db.child(childName).child('lectureSubjectList').get().val()
    if lectureSubjectList == None:
        lectureSubjectList = {}
    if not lectureID in lectureList:
      abort(400, message='lecture not found')
    if not subjectID in subjectList:
      abort(400, message='subject not found')
    for i in lectureSubjectList:
      if lectureSubjectList[i]['lectureID'] == lectureID and lectureSubjectList[i]['subjectID'] == subjectID:
        del lectureSubjectList[i]
        db.child(childName).child('lectureSubjectList').set(lectureSubjectList)
        break
    return lectureSubjectList

class GenerateTimeTable(Resource):
  def post(self, deptID):
    args=generateTimeTableParser.parse_args()
    semList = eval(args['semList'])
    departmentList = db.child(childName).child('departmentList').get().val()
    if departmentList == None:
        departmentList = {}
    lectureList = db.child(childName).child('lectureList').get().val()
    if lectureList == None:
        lectureList = {}
    if not deptID in departmentList:
      abort(400, message='department not found')
    for i in semList:
      if int(i) > departmentList[deptID]['semCount']:
        abort(400, message='semester out of range')
    subjectList = db.child(childName).child('subjectList').get().val()
    if subjectList == None:
        subjectList = {}
    tempSubjectList = []
    for i in semList:
      sList =[]
      for j in subjectList:
        if subjectList[j]['deptID'] == deptID and subjectList[j]['sem'] == int(i):
          sList.append({ 'subjectID' : j, 'cnt' : 0})
      tempSubjectList.append({'semester' : i, 'subjectList' : sList})
    weekHourList = []
    for i in semList:
      for j in tempSubjectList:
        if j['semester'] == i:
          sList = j['subjectList']
          totalWeekHour = 0
          for k in sList:
            totalWeekHour = totalWeekHour + subjectList[k['subjectID']]['hours']
          weekHourList.append({'semester' : i, 'weekHour' : totalWeekHour})
    invalidWeekHourList = []
    for i in weekHourList:
      if i['weekHour'] != 25:
        invalidWeekHourList.append(i['semester'])
    invalidWeekHourStr = ''
    if invalidWeekHourList != []:
      for i in invalidWeekHourList:
        invalidWeekHourStr = invalidWeekHourStr + 'semester ' + i + ', '
      abort(400, message=invalidWeekHourStr + 'total week hour of subjects is not 25')
    lectureSubjectList = db.child(childName).child('lectureSubjectList').get().val()
    if lectureSubjectList == None:
        lectureSubjectList = {}
    tempLectureSubjectList = []
    noLectureList = []
    for i in tempSubjectList:
      lecList =[]
      for j in i['subjectList']:
        flag = 0
        for k in lectureSubjectList:
          if lectureSubjectList[k]['subjectID'] == j['subjectID']:
            if lectureSubjectList[k]['lectureID'] in lectureList:
              lecList.append(k)
              flag = 1
        if flag == 0:
          if not i['semester'] in noLectureList:
            noLectureList.append(i['semester'])
      tempLectureSubjectList.append({'semester' : i['semester'], 'lectureSubjectList' : lecList})
    if noLectureList != []:
      semName = ''
      for i in noLectureList:
        semName = semName + 'semester ' + i + ', '
      abort(400, message=semName + 'have no lectures in some subjects')
    timeTable = {}
    for i in tempSubjectList:
      semTimeTable = {}
      tSubjectList = i['subjectList']
      weekCnt = 0
      hourCnt = 1
      weekList = ['mon','tue','wed','thu','fri']
      for j in tSubjectList:
        while (subjectList[j['subjectID']]['hours'] > j['cnt']):
          if weekCnt == 5:
            weekCnt = 0
            hourCnt += 1
          label = weekList[weekCnt] + '_' + str(hourCnt) + 'hr'
          semTimeTable[label] = j['subjectID']
          j['cnt'] += 1
          weekCnt += 1
        timeTable[i['semester']] = semTimeTable
    # print(timeTable)
    lectureOccupiedList = {}
    for i in timeTable:
      for j in timeTable[i]:
        subjectID = timeTable[i][j]
        # print("orginal",subjectID)
        flag = 0
        for k in lectureSubjectList:
          if lectureSubjectList[k]['subjectID'] == timeTable[i][j]:
            if lectureSubjectList[k]['lectureID'] in lectureList:
              lectureID = lectureSubjectList[k]['lectureID']
              day = j.split('_')[0]
              if lectureList[lectureID][day] == 'yes':
                if (lectureID not in lectureOccupiedList) or (j not in lectureOccupiedList[lectureID]):
                  flag = 1
                  break
        if flag == 1:
          timeTable[i][j] = { 'subjectID' : subjectID, 'subjectName' : subjectList[timeTable[i][j]]['name'], 'lectureID': lectureID, 'lectureName' : lectureList[lectureID]['name']  }
          if lectureID not in lectureOccupiedList:
            lectureOccupiedList[lectureID] = { j : subjectID }
          else:
            lectureOccupiedList[lectureID][j] = subjectID
        elif flag == 0:
          tsubjectlist = []
          for k in tempSubjectList:
            if k['semester'] == i:
              tsubjectlist = k['subjectList']
          subjectlist = []
          subjectlist = tsubjectlist.copy()
          for k in tsubjectlist:
            if k['subjectID'] == subjectID:
              subjectlist.remove(k)
              break
          flag = 0
          for sub in subjectlist:
            for l in lectureSubjectList:
              if lectureSubjectList[l]['subjectID'] == sub['subjectID']:
                if lectureSubjectList[l]['lectureID'] in lectureList:
                  replaceLectureID = lectureSubjectList[l]['lectureID']
                  day = j.split('_')[0]
                  if lectureList[replaceLectureID][day] == 'yes':
                    if (replaceLectureID not in lectureOccupiedList) or (j not in lectureOccupiedList[replaceLectureID]):
                      replaceSubjectID = sub['subjectID']
                      for m in timeTable[i]:
                        if timeTable[i][m] == sub['subjectID']:
                          for n in lectureSubjectList:
                            if lectureSubjectList[n]['subjectID'] == subjectID:
                              if lectureSubjectList[n]['lectureID'] in lectureList:
                                tlectureID = lectureSubjectList[n]['lectureID']
                                replaceDay = m.split('_')[0]
                                if lectureList[tlectureID][replaceDay] == 'yes':
                                  if (tlectureID not in lectureOccupiedList) or (m not in lectureOccupiedList[tlectureID]):
                                    timeTable[i][m] = subjectID
                                    timeTable[i][j] = replaceSubjectID
                                    timeTable[i][j] = { 'subjectID' : replaceSubjectID, 'subjectName' : subjectList[timeTable[i][j]]['name'], 'lectureID' : replaceLectureID, 'lectureName' : lectureList[replaceLectureID]['name']  }
                                    if replaceLectureID not in lectureOccupiedList:
                                      lectureOccupiedList[replaceLectureID] = { j : replaceSubjectID }
                                    else:
                                      lectureOccupiedList[replaceLectureID][j] = replaceSubjectID
                                    flag = 1
                                    # print("replace", replaceSubjectID)
                                    break
                          if flag == 1:
                            break
              if flag == 1:
                break
            if flag == 1:
                break
          if flag == 0:
            timeTable[i][j] = { 'lectureID' : 'nil', 'subjectID' : 'nil', 'subjectName' : "LIBRARY", 'lectureName' : "HOUR"  }
    timeTableDB = db.child(childName).child('timeTable').get().val()
    if timeTableDB == None:
        timeTableDB = {}
    dTimeTable = {}
    for i in timeTable:
      dTimeTable['semester ' + str(i)] = timeTable[i]
    timeTableDB[deptID] = dTimeTable
    db.child(childName).child('timeTable').set(timeTableDB)
    return timeTable

  def get(self, deptID):
    departmentList = db.child(childName).child('departmentList').get().val()
    if departmentList == None:
      departmentList = {}
    # lectureList = db.child(childName).child('lectureList').get().val()
    # if lectureList == None:
    #     lectureList = {}
    # subjectList = db.child(childName).child('subjectList').get().val()
    # if subjectList == None:
    #     subjectList = {}
    # lectureSubjectList = db.child(childName).child('lectureSubjectList').get().val()
    # if lectureSubjectList == None:
    #     lectureSubjectList = {}
    timeTableDB = db.child(childName).child('timeTable').get().val()
    if timeTableDB == None:
        timeTableDB = {}
    if deptID not in departmentList:
      abort(400, message='department not found')
    if deptID in timeTableDB:
      timeTable = timeTableDB[deptID]
      # for i in timeTable:
      #   for j in timeTable[i]:
      #     for k in lectureSubjectList:
      #       if lectureSubjectList[k]['subjectID'] == timeTable[i][j]:
      #         if lectureSubjectList[k]['lectureID'] in lectureList:
      #           lectureID = lectureSubjectList[k]['lectureID']
      #           break
      #     timeTable[i][j] = { 'subjectName' : subjectList[timeTable[i][j]]['name'], 'lectureName' : lectureList[lectureID]['name']  }
    else:
      timeTable = {}
    return timeTable

class LectureTimeTable(Resource):
  def get(self, lectureID):
    lectureList = db.child(childName).child('lectureList').get().val()
    if lectureList == None:
        lectureList = {}
    subjectList = db.child(childName).child('subjectList').get().val()
    if subjectList == None:
        subjectList = {}
    lectureSubjectList = db.child(childName).child('lectureSubjectList').get().val()
    if lectureSubjectList == None:
        lectureSubjectList = {}
    if lectureID not in lectureList:
      abort(400, message='lecture not found')
    timeTableDB = db.child(childName).child('timeTable').get().val()
    if timeTableDB == None:
        timeTableDB = {}
    if lectureList[lectureID]['deptID'] in timeTableDB:
      timeTable = timeTableDB[lectureList[lectureID]['deptID']]
      lectureTimeTable = {}
      # for i in timeTable:
      #   for j in timeTable[i]:
      #     for k in lectureSubjectList:
      #       if lectureSubjectList[k]['subjectID'] == timeTable[i][j]:
      #         if lectureSubjectList[k]['lectureID'] in lectureList:
      #           tLectureID = lectureSubjectList[k]['lectureID']
      #           break
      #     timeTable[i][j] = { 'subjectName' : subjectList[timeTable[i][j]]['name'], 'lectureID' : tLectureID, 'sem' : i  }
      hourList = ['mon_1hr', 'mon_2hr', 'mon_3hr', 'mon_4hr', 'mon_5hr',
                  'tue_1hr', 'tue_2hr', 'tue_3hr', 'tue_4hr', 'tue_5hr',
                  'wed_1hr', 'wed_2hr', 'wed_3hr', 'wed_4hr', 'wed_5hr',
                  'thu_1hr', 'thu_2hr', 'thu_3hr', 'thu_4hr', 'thu_5hr',
                  'fri_1hr', 'fri_2hr', 'fri_3hr', 'fri_4hr', 'fri_5hr']
      for i in hourList:
        flag = 0
        for j in timeTable:
          if timeTable[j][i]['lectureID'] == lectureID:
            lectureTimeTable[i] = timeTable[j][i]
            lectureTimeTable[i]['sem'] = 'SEM ' + str(subjectList[lectureTimeTable[i]['subjectID']]['sem'])
            flag = 1
            break
        if flag == 0:
          lectureTimeTable[i] = {'subjectName' : '', 'sem' : ''}
    else:
      lectureTimeTable = {}
    return lectureTimeTable


class feedbackReg(Resource):
  def post(self):
    args = feedbackParser.parse_args()
    feedbackList = db.child('AutomaticTimeTable').child('feedbackList').get().val()
    if feedbackList == None:
      feedbackList = {}
    feedbackcnt = db.child('AutomaticTimeTable').child('feedbackcnt').get().val()
    if feedbackcnt == None:
      feedbackcnt = 0
    feedbackcnt += 1
    db.child('AutomaticTimeTable').child('feedbackcnt').set(feedbackcnt)
    feedbackID ='FEEDBACK'+ str(100+feedbackcnt)    
    feedbackList[feedbackID] = args
    db.child('AutomaticTimeTable').child('feedbackList').set(feedbackList)
    return feedbackList

  def get(self):
    feedbackList = db.child('AutomaticTimeTable').child('feedbackList').get().val()
    if feedbackList == None:
      feedbackList = {}
    return feedbackList

api.add_resource(Login, '/login')
api.add_resource(DepartmentReg, '/department')
api.add_resource(DepartmentUpdate, '/department/<deptID>')
api.add_resource(SubjectReg, '/subject')
api.add_resource(SubjectUpdate, '/subject/<subjectID>')
api.add_resource(SubjectList, '/subjectList/<deptID>/<sem>')
api.add_resource(DepartmentSubjectList, '/deptSubjectList/<deptID>')
api.add_resource(LectureReg, '/lecture')
api.add_resource(LectureList, '/lectureList/<deptID>')
api.add_resource(LectureUpdate, '/lecture/<lectureID>')
api.add_resource(LectureSubject, '/lectureSubject/<lectureID>/<subjectID>')
api.add_resource(GenerateTimeTable, '/timeTable/<deptID>')
api.add_resource(LectureTimeTable, '/lectureTimeTable/<lectureID>')
api.add_resource(feedbackReg, '/feedback')

if __name__ == '__main__':
  app.run(debug=True, host='0.0.0.0', port=8000)