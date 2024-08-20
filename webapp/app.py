from flask import Flask,render_template, request, make_response, redirect, url_for,session
import requests

app=Flask(__name__)
app.secret_key='abcd'

base_url='http://127.0.0.1:8000'

@app.route('/admin')
def adminHome():
	warning=request.cookies.get('warning')
	if warning == None:
		warning = ''
	if 'admin' in session:
		response = requests.get(base_url+'/department')
		departmentList = response.json()
		return render_template('admin_home.html', departmentList=departmentList, warning=warning)
	else:
		return render_template('login.html', session='admin', warning=warning)

@app.route('/lecture')
def lectureHome():
	if 'lecture' in session:
		lectureID = session['lecture']
		response = requests.get(base_url+'/lecture/' + lectureID)
		lectureDetails = response.json()
		response = requests.get(base_url+'/lectureSubject/' + lectureID + '/nil')
		lectureSubjects = response.json()
		response = requests.get(base_url + '/lectureTimeTable/' + lectureID)
		timeTable = response.json()
		return render_template('lecture_home.html', lectureDetails=lectureDetails, lectureSubjects=lectureSubjects, timeTable=timeTable)
	else:
		warning=request.cookies.get('warning')
		if warning == None:
			warning = ''
		return render_template('login.html', session='lecture', warning=warning)

@app.route('/')
def userHome():
	response = requests.get(base_url+'/department')
	departmentList = response.json()
	return render_template('user_home.html', departmentList=departmentList)

@app.route('/userfeedback')
def userfeedback():
		return render_template('user_feedback.html')

@app.route('/feedbackregistration', methods=['POST','GET'])
def feedbackReg():
	if request.method == 'POST':
		userInput = request.form.to_dict()
		response = requests.post(base_url + '/feedback', data = userInput)
		if response.status_code == 400:
			resp=make_response(redirect(url_for('userfeedback')))
			resp.set_cookie('warning',str(response.json()['message']), max_age=5)
			return resp
		return redirect(url_for('userHome'))

@app.route('/login', methods=['POST', 'GET'])
def login():
	if request.method == 'POST':
		userInput = request.form.to_dict()
		response = requests.post(base_url+'/login', data = userInput)
		loginID = response.json()
		if userInput['cat'] == 'admin':
			if loginID == 'admin':
				session['admin'] = 'admin'
				return redirect(url_for('adminHome'))
			else:
				resp=make_response(redirect(url_for('adminHome')))
				resp.set_cookie('warning','invalid email or password', max_age=5)
				return resp
		if userInput['cat'] == 'lecture':
			if loginID != 'invalid':
				session['lecture'] = loginID
				return redirect(url_for('lectureHome'))
			else:
				resp=make_response(redirect(url_for('lectureHome')))
				resp.set_cookie('warning','invalid email or password', max_age=5)
				return resp

@app.route('/adminLogout')
def adminLogout():
	if 'admin' in session:
		session.pop('admin', None)
	return redirect(url_for('adminHome'))

@app.route('/lectureLogout')
def lectureLogout():
	if 'lecture' in session:
		session.pop('lecture', None)
	return redirect(url_for('lectureHome'))

@app.route('/departmentReg', methods=['POST','GET'])
def departmentReg():
	if 'admin' in session:
		if request.method == 'POST':
			userInput = request.form.to_dict()
			response = requests.post(base_url+'/department', data=userInput)
			if response.status_code == 200:
				resp=make_response(redirect(url_for('adminHome')))
				resp.set_cookie('warning','department successfully registered', max_age=5)
				return resp
			elif response.status_code == 400:
				resp=make_response(redirect(url_for('adminHome')))
				resp.set_cookie('warning',response.json()['message'], max_age=5)
				return resp
	return redirect(url_for('adminHome'))

@app.route('/departmentUpdate', methods=['POST','GET'])
def departmentUpdate():
	if 'admin' in session:
		if request.method == 'POST':
			userInput = request.form.to_dict()
			response = requests.put(base_url+'/department/' + userInput['deptID'], data=userInput)
			if response.status_code == 200:
				resp=make_response(redirect(url_for('adminHome')))
				resp.set_cookie('warning','department successfully updated', max_age=5)
				return resp
			elif response.status_code == 400:
				resp=make_response(redirect(url_for('adminHome')))
				resp.set_cookie('warning',response.json()['message'], max_age=5)
				return resp
	return redirect(url_for('adminHome'))

@app.route('/departmentDelete', methods=['POST','GET'])
def departmentDelete():
	if 'admin' in session:
		if request.method == 'POST':
			userInput = request.form.to_dict()
			response = requests.delete(base_url+'/department/' + userInput['deptID'])
			if response.status_code == 200:
				resp=make_response(redirect(url_for('adminHome')))
				resp.set_cookie('warning','department successfully deleted', max_age=5)
				return resp
	return redirect(url_for('adminHome'))

@app.route('/departmentSemesterList/<deptID>')
def departmentSemesterList(deptID):
	if 'admin' in session:
		response = requests.get(base_url+'/department')
		departmentList = response.json()
		departmentDetails = departmentList[deptID]
		semesterList = []
		for i in range(1, departmentDetails['semCount']+1):
			semesterList.append({'semester' : i, 'semName' : 'SEMESTER ' + str(i)})
		return render_template('admin_semester_list.html', deptID=deptID, departmentDetails=departmentDetails, semesterList=semesterList)
	else:
		return redirect(url_for('adminHome'))

@app.route('/subjectList/<deptID>/<semester>')
def subjectList(deptID,semester):
	if 'admin' in session:
		warning=request.cookies.get('warning')
		if warning == None:
			warning = ''
		response = requests.get(base_url+'/department')
		departmentList = response.json()
		departmentDetails = departmentList[deptID]
		response = requests.get(base_url+'/subjectList/'+ deptID + '/' + semester)
		subjectList = response.json()
		return render_template('admin_subject_list.html', deptID=deptID, semester=semester, departmentDetails=departmentDetails, subjectList=subjectList, warning=warning)
	else:
		return redirect(url_for('adminHome'))

@app.route('/subjectReg', methods=['POST','GET'])
def subjectReg():
	if 'admin' in session:
		if request.method == 'POST':
			userInput = request.form.to_dict()
			response = requests.post(base_url+'/subject', data=userInput)
			if response.status_code == 200:
				resp=make_response(redirect(url_for('subjectList', deptID=userInput['deptID'], semester=userInput['sem'])))
				resp.set_cookie('warning','subject successfully registered', max_age=5)
				return resp
			elif response.status_code == 400:
				resp=make_response(redirect(url_for('subjectList', deptID=userInput['deptID'], semester=userInput['sem'])))
				resp.set_cookie('warning',response.json()['message'], max_age=5)
				return resp
	return redirect(url_for('adminHome'))

@app.route('/subjectUpdate', methods=['POST','GET'])
def subjectUpdate():
	if 'admin' in session:
		if request.method == 'POST':
			userInput = request.form.to_dict()
			response = requests.put(base_url+'/subject/' + userInput['subjectID'], data=userInput)
			if response.status_code == 200:
				resp=make_response(redirect(url_for('subjectList', deptID=userInput['deptID'], semester=userInput['sem'])))
				resp.set_cookie('warning','subject successfully updated', max_age=5)
				return resp
			elif response.status_code == 400:
				resp=make_response(redirect(url_for('subjectList', deptID=userInput['deptID'], semester=userInput['sem'])))
				resp.set_cookie('warning',response.json()['message'], max_age=5)
				return resp
	return redirect(url_for('adminHome'))

@app.route('/subjectDelete', methods=['POST','GET'])
def subjectDelete():
	if 'admin' in session:
		if request.method == 'POST':
			userInput = request.form.to_dict()
			response = requests.delete(base_url+'/subject/' + userInput['subjectID'])
			if response.status_code == 200:
				resp=make_response(redirect(url_for('subjectList', deptID=userInput['deptID'], semester=userInput['sem'])))
				resp.set_cookie('warning','subject successfully deleted', max_age=5)
				return resp
	return redirect(url_for('adminHome'))


@app.route('/adminfeedbacklist')
def adminfeedbacklist():
	if 'admin' in session:
		response = requests.get(base_url+'/feedback')
		feedbacklist = response.json()
		return render_template('admin_feedbacklist.html',feedbacklist=feedbacklist)
	else:
		return render_template('admin_login.html', session='admin')

@app.route('/lectureList/<deptID>')
def lectureList(deptID):
	if 'admin' in session:
		warning=request.cookies.get('warning')
		if warning == None:
			warning = ''
		response = requests.get(base_url+'/department')
		departmentList = response.json()
		departmentDetails = departmentList[deptID]
		response = requests.get(base_url+'/lectureList/' + deptID)
		lectureList = response.json()
		return render_template('admin_lecture_list.html', deptID=deptID, departmentDetails=departmentDetails, lectureList=lectureList, warning=warning)
	else:
		return redirect(url_for('adminHome'))

@app.route('/lectureReg', methods=['GET','POST'])
def lectureReg():
	if 'admin' in session:
		if request.method=='POST':
			userInput=request.form.to_dict()
			userImg = request.files['photo']
			files = {'photo' : (userImg.filename, userImg, userImg.content_type)}
			userInput['sun'] = 'yes'
			userInput['mon'] = 'yes'
			userInput['tue'] = 'yes'
			userInput['wed'] = 'yes'
			userInput['thu'] = 'yes'
			userInput['fri'] = 'yes'
			userInput['sat'] = 'yes'
			response = requests.post(base_url + '/lecture', data=userInput, files=files)
			if response.status_code == 200:
				resp=make_response(redirect(url_for('lectureList', deptID=userInput['deptID'])))
				resp.set_cookie('warning','lecture successfully registered', max_age=5)
				return resp
			elif response.status_code == 400:
				resp=make_response(redirect(url_for('lectureList', deptID=userInput['deptID'])))
				resp.set_cookie('warning',response.json()['message'], max_age=5)
				return resp
			return redirect(url_for('lectureList', deptID=userInput['deptID']))
	return redirect(url_for('adminHome'))

@app.route('/adminLectureProfile/<lectureID>')
def adminLectureProfile(lectureID):
	if 'admin' in session:
		warning=request.cookies.get('warning')
		if warning == None:
			warning = ''
		response = requests.get(base_url+'/lecture/' + lectureID)
		lectureDetails = response.json()
		response = requests.get(base_url+'/deptSubjectList/' + lectureDetails['deptID'])
		subjectList = response.json()
		response = requests.get(base_url+'/lectureSubject/' + lectureID + '/nil')
		lectureSubjects = response.json()
		return render_template('admin_lecture_profile.html', lectureID=lectureID, lectureDetails=lectureDetails, subjectList=subjectList, lectureSubjects=lectureSubjects, warning=warning)
	else:
		return redirect(url_for('adminHome'))

@app.route('/editLectureProfile/<lectureID>')
def editLectureProfile(lectureID):
	if 'admin' in session:
		response = requests.get(base_url+'/lecture/' + lectureID)
		lectureDetails = response.json()
		return render_template('edit_lecture_profile.html', lectureID=lectureID, lectureDetails=lectureDetails)
	else:
		return redirect(url_for('adminHome'))

@app.route('/updateLectureProfile', methods=['POST','GET'])
def updateLectureProfile():
	if 'admin' in session:
		if request.method == 'POST':
			userInput = request.form.to_dict()
			userImg = request.files['photo']
			if userImg:
				files = {'photo' : (userImg.filename, userImg, userImg.content_type)}
				response = requests.put(base_url + '/lecture/' + userInput['lectureID'], data=userInput, files=files)
			else:
				response = requests.put(base_url + '/lecture/' + userInput['lectureID'], data=userInput)
			if response.status_code == 200:
				resp=make_response(redirect(url_for('adminLectureProfile', lectureID = userInput['lectureID'])))
				resp.set_cookie('warning','lecture profile successfully updated', max_age=5)
				return resp
	return redirect(url_for('adminHome'))

@app.route('/updateLecture', methods=['POST','GET'])
def updateLecture():
	if 'admin' in session:
		if request.method == 'POST':
			userInput = request.form.to_dict()
			requests.put(base_url + '/lecture/' + userInput['lectureID'], data=userInput)
			return redirect(url_for('adminLectureProfile', lectureID = userInput['lectureID']))
	else:
		return redirect(url_for('adminHome'))

@app.route('/addLectureSubjects', methods=['POST','GET'])
def addLectureSubjects():
	if 'admin' in session:
		if request.method == 'POST':
			userInput = request.form.to_dict()
			response = requests.post(base_url + '/lectureSubject/' + userInput['lectureID'] + '/' + userInput['subjectID'])
			if response.status_code == 200:
				resp=make_response(redirect(url_for('adminLectureProfile', lectureID = userInput['lectureID'])))
				resp.set_cookie('warning','subjected added  successfully to lecture', max_age=5)
				return resp
	else:
		return redirect(url_for('adminHome'))

@app.route('/deleteLectureSubjects', methods=['POST','GET'])
def deleteLectureSubjects():
	if 'admin' in session:
		if request.method == 'POST':
			userInput = request.form.to_dict()
			response = requests.delete(base_url + '/lectureSubject/' + userInput['lectureID'] + '/' + userInput['subjectID'])
			if response.status_code == 200:
				resp=make_response(redirect(url_for('adminLectureProfile', lectureID = userInput['lectureID'])))
				resp.set_cookie('warning','subjected deleted  successfully from lecture', max_age=5)
				return resp
	else:
		return redirect(url_for('adminHome'))

@app.route('/deleteLecture', methods=['POST','GET'])
def deleteLecture():
	if 'admin' in session:
		if request.method == 'POST':
			userInput = request.form.to_dict()
			response = requests.get(base_url+'/lecture/' + userInput['lectureID'])
			lectureDetails = response.json()
			requests.delete(base_url + '/lecture/' + userInput['lectureID'])
			return redirect(url_for('lectureList', deptID=lectureDetails['deptID']))
	return redirect(url_for('adminHome'))

@app.route('/adminSemSelection/<deptID>')
def adminSemSelection(deptID):
	if 'admin' in session:
		response = requests.get(base_url+'/department')
		departmentList = response.json()
		departmentDetails = departmentList[deptID]
		semesterList = []
		for i in range(1, departmentDetails['semCount']+1):
			semesterList.append({'semester' : i, 'semName' : 'SEMESTER ' + str(i)})
		response = requests.get(base_url + '/timeTable/' + deptID)
		timeTable = response.json()
		warning=request.cookies.get('warning')
		if warning == None:
			warning = ''
		return render_template('admin_sem_selection.html', deptID=deptID, departmentDetails=departmentDetails, semesterList=semesterList, timeTable=timeTable, warning=warning)
	else:
		return render_template(url_for('adminHome'))

@app.route('/adminGenerateTimeTable', methods=['POST', 'GET'])
def adminGenerateTimeTable():
	if 'admin' in session:
		if request.method == 'POST':
			semList = request.form.getlist('semList')
			userInput = request.form.to_dict()
			if semList == []:
				return redirect(url_for('adminSemSelection', deptID=userInput['deptID']))
			else:
				semList = str(semList)
				userInput['semList'] = semList
				response = requests.post(base_url + '/timeTable/' + userInput['deptID'], data = userInput)
				if response.status_code == 400:
					warning = response.json()['message']
					resp=make_response(redirect(url_for('adminSemSelection', deptID=userInput['deptID'])))
					resp.set_cookie('warning',warning, max_age=5)
					return resp
				elif response.status_code == 200:
					timeTable = response.json()
					response = requests.get(base_url+'/department')
					departmentList = response.json()
					departmentDetails = departmentList[userInput['deptID']]
					return render_template('admin_time_table.html', deptID=userInput['deptID'], departmentDetails=departmentDetails, timeTable=timeTable)
	else:
		return render_template(url_for('adminHome'))

@app.route('/userDeptSemesterList/<deptID>')
def userDeptSemesterList(deptID):
	response = requests.get(base_url+'/department')
	departmentList = response.json()
	departmentDetails = departmentList[deptID]
	semesterList = []
	for i in range(1, departmentDetails['semCount']+1):
		semesterList.append({'semester' : i, 'semName' : 'SEMESTER ' + str(i)})
	return render_template('user_semester_list.html', deptID=deptID, departmentDetails=departmentDetails, semesterList=semesterList)

@app.route('/userSubjectList/<deptID>/<semester>')
def userSubjectList(deptID,semester):
	response = requests.get(base_url+'/department')
	departmentList = response.json()
	departmentDetails = departmentList[deptID]
	response = requests.get(base_url+'/subjectList/'+ deptID + '/' + semester)
	subjectList = response.json()
	return render_template('user_subject_list.html', deptID=deptID, semester=semester, departmentDetails=departmentDetails, subjectList=subjectList)

@app.route('/userLectureList/<deptID>')
def userLectureList(deptID):
	response = requests.get(base_url+'/department')
	departmentList = response.json()
	departmentDetails = departmentList[deptID]
	response = requests.get(base_url+'/lectureList/' + deptID)
	lectureList = response.json()
	return render_template('user_lecture_list.html', deptID=deptID, departmentDetails=departmentDetails, lectureList=lectureList)

@app.route('/userLectureProfile/<lectureID>')
def userLectureProfile(lectureID):
	response = requests.get(base_url+'/lecture/' + lectureID)
	lectureDetails = response.json()
	response = requests.get(base_url+'/deptSubjectList/' + lectureDetails['deptID'])
	subjectList = response.json()
	response = requests.get(base_url+'/lectureSubject/' + lectureID + '/nil')
	lectureSubjects = response.json()
	return render_template('user_lecture_profile.html', lectureID=lectureID, lectureDetails=lectureDetails, subjectList=subjectList, lectureSubjects=lectureSubjects)

@app.route('/userTimeTable/<deptID>')
def userTimeTable(deptID):
	response = requests.get(base_url+'/department')
	departmentList = response.json()
	departmentDetails = departmentList[deptID]
	response = requests.get(base_url + '/timeTable/' + deptID)
	timeTable = response.json()
	return render_template('user_time_table.html', departmentDetails=departmentDetails, timeTable=timeTable)


if __name__=='__main__':
	app.run(debug=True, host='0.0.0.0')