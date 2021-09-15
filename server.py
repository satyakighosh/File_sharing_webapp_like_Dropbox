'''
A FLASK MINIMAL APP:

from flask import Flask, abort

app = Flask(__name__)

@app.route("/")
def hello_world():
    return abort(404)
    #return "<p>Hello, World!</p>"

'''

from flask import (
	Flask,
	abort,
	render_template, 
	request, 
	redirect, 
	session,
	send_file
)
import pymongo
from flask_pymongo import PyMongo
import json
from cfg import config
from utils import get_random_string,allowed_file
from hashlib import sha256
from datetime import datetime
from werkzeug.utils import secure_filename
from bson.objectid import ObjectId
import os



app = Flask(__name__)
app.config["MONGO_URI"] = config['mongouri']
app.config['UPLOAD_FOLDER'] = '/home/satyaki/Work/mycloud/uploads'
mongo = PyMongo(app)

app.secret_key = b'djojfld#$%#$^dlsjf'

@app.route('/')
def show_index():
	if not 'userToken' in session:
		session['error'] = 'You must log in to access this page!'
		return redirect('/login')

	# validate user-token
	token_document = mongo.db.user_tokens.find_one({
		'sessionHash' : session['userToken']
	})
	

	if token_document is None:
		session.pop('userToken', None)
		session['error'] = 'You must log in to access this page!'
		return redirect('/login')

	error = ''
	if 'error' in session:
		error = session['error']
		session.pop('error', None)
	

	userID = token_document['userID']

	user = mongo.db.users.find_one({
		'_id' : userID
	})

	uploaded_files = mongo.db.files.find({
		'userID' : userID,
		'isActive' : True
	}).sort([("createdAt", pymongo.DESCENDING)])

	return render_template(
		'files.html',
		uploaded_files = uploaded_files,
		user = user,
		error=error
	)


@app.route('/login')
def show_login():
	signupSuccess = ''
	error = ''

	if 'signupSuccess' in session:
		signupSuccess = session['signupSuccess']
		session.pop('signupSuccess', None)

	if 'error' in session:
		error = session['error']
		session.pop('error', None)
	return render_template('login.html', signupSuccess = signupSuccess, error=error)


@app.route('/check_login', methods=['POST'])
def check_login():
	try:
		email = request.form['email']
	except Keyerror:
		email = ''
	try:
		password = request.form['password']
	except Keyerror:
		password = ''

	# check if email is blank
	if not len(email) > 0:
		session['error'] = 'Email is required'
		return redirect('/login')

	# check if password is blank
	if not len(password) > 0:
		session['error'] = 'Password is required'
		return redirect('/login')

	# find user in database
	user_document = mongo.db.users.find_one({"email" : email})
	if user_document is None:
		# if user not in database, throw error
		session['error'] = 'No account exists with this email address'
		return redirect('/login')

	# verify the password hash
	password_hash = sha256(password.encode('utf-8')).hexdigest()
	if user_document['password'] != password_hash:
		session['error'] = 'Password is wrong'
		return redirect('/login')

	# generate token and save it in session
	randomstring = get_random_string()
	randomSessionHash =  sha256(randomstring.encode('utf-8')).hexdigest()
	token_object = mongo.db.user_tokens.insert_one({
		'userID' : user_document['_id'],
		'sessionHash' : randomSessionHash,
		'createdAt': datetime.utcnow()
	})

	session['userToken'] = randomSessionHash

	redirectToUrl = ''
	if 'redirectToUrl' in session:
		redirectToUrl = session['redirectToUrl']
		session.pop('redirectToUrl', None)
		return redirect(redirectToUrl)
		
	# redirect to '/'
	return redirect('/')



@app.route('/signup')
def show_signup():
	error = ''
	if 'error' in session:
		error = session['error']
		session.pop('error', None)
	return render_template('signup.html', error = error)   


@app.route('/handle_signup', methods=['POST'])
def handle_signup():
	try:
		email = request.form['email']
	except Keyerror:
		email = ''
	try:
		password = request.form['password']
	except Keyerror:
		password = ''
	try:
		confirm_password = request.form['confirm_password']
	except Keyerror:
		confirm_password = ''
	
	# to be removed after debugging 
	#print('EMAIL is ' + email)
	#print('PASSWORD is ' + password)
	#print('CONFIRM_PASSWORD is ' + confirm_password)

	# check if email is blank
	if not len(email) > 0:
		session['error'] = 'Email is required'
		return redirect('/signup')

	# check if email is valid
	if not '@' in email or not '.' in email:
		session['error'] = 'Email is invalid'
		return redirect('/signup')

	# check if password is blank
	if not len(password) > 0:
		session['error'] = 'Password is required'
		return redirect('/signup')

	# check if confirm_password is blank
	if not len(confirm_password) > 0:
		session['error'] = 'Confirm Password'
		return redirect('/signup')

	# check if password matches confirm_password
	if password != confirm_password:
		session['error'] = 'Passwords do not match'
		return redirect('/signup')

	# check if email already exists
	matching_user_count = mongo.db.users.count_documents({"email" : email})
	if matching_user_count > 0:
		session['error'] = 'Email already exists'
		return redirect('/signup')

	# create user-record in database
	password = sha256(password.encode('utf-8')).hexdigest()
	result = mongo.db.users.insert_one({
		'email' : email,
		'password': password,
		'name':'',
		'lastLoginDate': None,
		'createdAt': datetime.utcnow(),
		'updatedAt': datetime.utcnow()
	})
	
	# redirect to login page
	session['signupSuccess'] = 'Your user account is ready. You can login now.'
	return redirect('/login')


@app.route('/logout')
def logout_user():
	session.pop('userToken', None)
	session['signupSuccess'] = 'You have successfully logged out.'
	return redirect('/login')


@app.route('/handle_file_upload', methods=['POST'])
def handle_file_upload():
	if not 'userToken' in session:
		session['error'] = 'You must log in to access this page!'
		return redirect('/login')

	# validate user-token
	token_document = mongo.db.user_tokens.find_one({
		'sessionHash' : session['userToken']
	})
	

	if token_document is None:
		session.pop('userToken', None)
		session['error'] = 'You must log in to access this page!'
		return redirect('/login')


	if 'uploadedFile' not in request.files:
		session['error'] = 'No file uploaded'
		return redirect('/')
	

	file = request.files['uploadedFile']
	print(file)

	if file.filename == '':
		session['error'] = 'No selected file'
		return redirect('/')
    
	if not allowed_file(file.filename):
		session['error'] = 'File type not allowed'
		return redirect('/')
	
	maxFileSize = 20*1024*1024 #20 MB
	blob = file.read()
	fileSize = len(blob)
	
	if fileSize > maxFileSize:
		session['error'] = 'File size limit exceeded'
		return redirect('/')

	extension = file.filename.rsplit('.', 1)[1].lower()
	filename = secure_filename(file.filename)
	filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
	file.seek(0) # putting cursor at the beginning as it was already read once into blob
	file.save(filepath)

	
	print(fileSize)

	result = mongo.db.files.insert_one({
		'userID' : token_document['userID'],
		'originalFileName' : file.filename,
		'fileType' : extension,
		'fileSize' : fileSize,
		#'fileHash' : sha256(open(filepath).read().encode('utf-8')).hexdigest(),
		'fileHash' : sha256(blob).hexdigest(),
		'filePath' : filepath,
		'isActive' : True,
		'createdAt': datetime.utcnow()
	})

	return redirect('/')


@app.route('/download/<fileId>/<fileNameSlugified>', methods=['GET'])
def showDownloadPage(fileId, fileNameSlugified):
	print("FileId is " + fileId)

	# if user-token in session or not; no user-token means no user is logged in
	if not 'userToken' in session:
		session['error'] = 'You must log in to access this page!'
		session['redirectToUrl'] = '/download/' + fileId + '/' + fileNameSlugified
		return redirect('/login')

	# if a user-token is present, we validate the user-token to see if the session is valid
	token_document = mongo.db.user_tokens.find_one({
		'sessionHash' : session['userToken']
	})
	
	# if session is not valid, we send the user to the login page
	if token_document is None:
		session.pop('userToken', None)
		session['error'] = 'You must log in to access this page!'
		return redirect('/login')

	# at this point, the user is logged in
	# now we check if the file to be downloaded actually exists in the database
	userID = token_document['userID']

	user = mongo.db.users.find_one({
		'_id' : userID
	})

	file_object=None
	try:
		file_object = mongo.db.files .find_one({
			'_id' : ObjectId(fileId),
		})
	except:
		pass

	if file_object is None:
		return abort(404)

	print(file_object)
	return render_template(
		'download.html', 
		file=file_object, 
		user=user)



@app.route('/download_file/<fileId>', methods=['GET'])
def downloadFile(fileId):
	print("FileId is " + fileId)

	# if user-token in session or not; no user-token means no user is logged in
	if not 'userToken' in session:
		session['error'] = 'You must log in to access this page!'
		session['redirectToUrl'] = '/download_file/' + fileId
		return redirect('/login')

	# if a user-token is present, we validate the user-token to see if the session is valid
	token_document = mongo.db.user_tokens.find_one({
		'sessionHash' : session['userToken']
	})
	
	# if session is not valid, we send the user to the login page
	if token_document is None:
		session.pop('userToken', None)
		session['error'] = 'You must log in to access this page!'
		return redirect('/login')
	
	# check if file exists or not
	file_object=None
	try:
		file_object = mongo.db.files .find_one({
			'_id' : ObjectId(fileId),
		})
	except:
		pass

	if file_object is None:
		return abort(404)

	# Track user download
	userID = token_document['userID']

	mongo.db.file_downloads.insert_one({
		'fileId' : file_object['_id'],
		'userID' : userID,
		'createdAt' : datetime.utcnow(),
	})


	filePath = file_object['filePath']
	return send_file(filePath, as_attachment=True)
	#return "downloading...."