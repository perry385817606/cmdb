#!/usr/bin/python27
#encoding=utf-8

from flask import Flask
from flask import render_template
from flask import request
from flask import redirect
from flask import session
import json

import models

app = Flask(__name__)
# os.urandom(32) 可生成随机字符串，openssl也可以生成 
app.secret_key = '\xe7V(t\x00ub\x90\x85\x89_\xb8@\x84\xbfx\xf5{\xc0\x8a\x19!2fJS\xdb=\xff\x87\x13\xed'

@app.route('/')
def index():
	if session.get('user'): return redirect('/user/')

	return render_template('index.html')

#################### user login,logout,,add,delete,select,change ##################

@app.route('/login/',methods=['POST','GET'])
def login():
	if session.get('user'): return redirect('/user/')

	params = request.form if 'POST' == request.method else request.args
	username = params.get('username','')
	password = params.get('password','')

	user = models.validate_login(username,password)
	print user 	 # {'id': 1L, 'name': u'fj'}
	if user:
		session['user'] = user 
		print session['user']      # {'id': 1L, 'name': u'fj'}
		return redirect('/user/')
	else:
		return render_template('index.html', username=username, password=password, error='username or password is error')

@app.route('/logout/')
def logout():
	#print session.get('user'),session['user']
	session.clear()
	print session.get('user')
	return redirect('/')


@app.route('/test/')
def test():
	return render_template('test.html')

@app.route('/user/')
def users():
	if session.get('user') is None:
		return redirect('/')

	users = models.get_user()
	#print users
	return render_template('user.html',users=users)


# 用户编辑 ajax
@app.route('/user/list/')
def user_list():
	users = models.get_user()
	#print users
	return json.dumps({'data' : users})


@app.route('/user/add/')
def user_add():
	print session.get('user')
	if session.get('user') is None:
		return redirect('/')

	return render_template('user_add.html')


@app.route('/user/save/',methods=['POST'])
def user_save():
	if session.get('user') is None: return redirect('/')
	print request.form
	print request.form.get('birthday')	#get获得的是字符串,只能获得一个值
	print request.form.get('hobby')
	print '-' * 50
	print request.form.getlist('birthday')	#getlist获得的是列表，可以获取多个值
	print request.form.getlist('hobby')

	params = request.form if 'POST' == request.method else request.args

	username = params.get('username','')
	age = params.get('age','')
	password = params.get('password','')
	department = params.get('department','')
	sex = params.get('sex',0)
	hobby = request.form.getlist('hobby')
	detail = params.get('detail','')
	homepage = params.get('homepage','')
	birthday = params.get('birthday','')
	email = params.get('email','')

	ok,error = models.validate_user_save(username,age,password)
	if ok:
		models.user_save(username,age,password,department,sex,hobby,detail,homepage,birthday,email)
		return redirect('/user/')
	else:
		return render_template('user_add.html',username=username,age=age,password=password,error=error)


@app.route('/user/save/json/',methods=['POST'])
def user_save_json():
	if session.get('user') is None: return redirect('/')
	# print request.form
	# return json.dumps({'abc':1})
	print request.form.get('birthday')	#get获得的是字符串,只能获得一个值
	print request.form.get('hobby')
	print '-' * 50
	print request.form.getlist('birthday')	#getlist获得的是列表，可以获取多个值
	print request.form.getlist('hobby')

	params = request.form if 'POST' == request.method else request.args

	username = params.get('username','')
	age = params.get('age','')
	password = params.get('password','')
	department = params.get('department','')
	sex = params.get('sex',0)
	hobby = request.form.getlist('hobby')
	detail = params.get('detail','')
	homepage = params.get('homepage','')
	birthday = params.get('birthday','')
	email = params.get('email','')

	ok,error = models.validate_user_save(username,age,password)
	if ok:
		models.user_save(username,age,password,department,sex,hobby,detail,homepage,birthday,email)
		return json.dumps({'code':200})
	else:
		return json.dumps({'code':400,'error':error})


@app.route('/user/view/',methods=['GET'])
def user_view():
	if session.get('user') is None:
		return redirect('/')
	
	params = request.form if 'POST' == request.method else request.args
	id = params.get('id',0)
	user = models.get_user_by_id(id)	#通过id获取用户的信息，再通过模板传给user_view.html,从而在修改页面显示用户的信息
	print user
	return render_template('user_view.html',id = user.get('id',''), username = user.get('name',0), age = user.get('age',0))


@app.route('/user/view/json/',methods=['GET'])
def user_view_json():
	if session.get('user') is None:
		return redirect('/')
	
	params = request.form if 'POST' == request.method else request.args
	id = params.get('id',0)
	user = models.get_user_by_id(id)	#通过id获取用户的信息，再通过模板传给user_view.html,从而在修改页面显示用户的信息
	print user
	return json.dumps(user)
	

@app.route('/user/modify/',methods=['POST','GET'])
def user_modify():
	if session.get('user') is None:
		return redirect('/')

	params = request.form if 'POST' == request.method else request.args
	uid = params.get('id',0)
	username = params.get('username','')
	age = params.get('age','')
	department = params.get('department','')
	sex = params.get('sex',0)
	hobby = request.form.getlist('hobby')
	detail = params.get('detail','')
	homepage = params.get('homepage','')
	birthday = params.get('birthday','')
	email = params.get('email','')

	# print '-' * 60
	# print uid,username,age,department,sex,hobby,detail,homepage,birthday,email
	# print type(uid),type(username),type(age),type(department),type(sex),type(hobby),type(detail),type(homepage),type(birthday),type(email)
	# print '-' * 60
	ok,error = models.validate_user_modify(uid,username,age,detail,homepage,email)
	if ok:
		models.user_modify(uid,username,age,department,sex,hobby,detail,homepage,birthday,email)
		return redirect('/user/')
	else:
		return render_template('user_view.html',username=username,age=age,error=error)


@app.route('/user/modify/json/',methods=['POST','GET'])
def user_modify_json():
	if session.get('user') is None:
		return redirect('/')

	params = request.form if 'POST' == request.method else request.args
	uid = params.get('id',0)
	username = params.get('username','')
	age = params.get('age','')
	department = params.get('department','')
	sex = params.get('sex',0)
	hobby = request.form.getlist('hobby')
	detail = params.get('detail','')
	homepage = params.get('homepage','')
	birthday = params.get('birthday','')
	email = params.get('email','')

	# print '-' * 60
	# print uid,username,age,department,sex,hobby,detail,homepage,birthday,email
	# print type(uid),type(username),type(age),type(department),type(sex),type(hobby),type(detail),type(homepage),type(birthday),type(email)
	# print '-' * 60
	ok,error = models.validate_user_modify(uid,username,age,detail,homepage,email)
	if ok:
		models.user_modify(uid,username,age,department,sex,hobby,detail,homepage,birthday,email)
		return json.dumps({'code':200})
	else:
		return json.dumps({'code':400,'error':error})


@app.route('/user/delete/')
def user_delete():
	if session.get('user') is None:
		return redirect('/')

	uid = request.args.get('id',0)
	ok,error = models.user_delete(uid)
	if ok:
		return redirect('/user/')
	else:
		return error



#################### assets add,delete,select,change ##################

@app.route('/assets/')
def asset_index():
	if session.get('user') is None: return redirect('/')
	machine_rooms = models.get_machine_room()
	return render_template('asset.html',machine_rooms = machine_rooms)


@app.route('/assets/list/')
def asset_list():
	assets = models.get_assets()
	print assets
	return json.dumps({'data' : assets})


@app.route('/asset/view/')
def asset_view():
	aid = request.args.get('id',0)
	asset = models.get_asset_by_id(aid)
	print asset
	print '*' * 60
	print json.dumps(asset)
	return json.dumps(asset)


@app.route('/asset/modify/',methods=['post'])
def asset_modify():
	return json.dumps({'error':''})


@app.route('/asset/save/json/',methods=['post'])
def asset_save_json():
	params = request.form if 'POST' == request.method else request.args

	sn = params.get('sn','')
	hostname = params.get('hostname','')
	ip = params.get('ip','')
	os = params.get('os','')
	machine_room_id = params.get('machine_room_id','')
	vendor = params.get('vendor','')
	model = params.get('model','')
	ram = params.get('ram','')
	cpu = params.get('cpu','')
	disk = params.get('disk','')
	time_on_shelves = params.get('time_on_shelves','')
	over_guaranteed_date = params.get('over_guaranteed_date','')
	buiness = params.get('buiness','')
	admin = params.get('admin','')
	status = params.get('status','')
	print sn,hostname,ip,os,machine_room_id,vendor,model,ram,cpu,disk,time_on_shelves,over_guaranteed_date,buiness,admin,status
	print type(time_on_shelves),type(over_guaranteed_date)
	ok,error = models.validate_asset_save(sn)
	if ok:
		models.asset_save(sn,hostname,ip,os,machine_room_id,vendor,model,ram,cpu,disk,time_on_shelves,over_guaranteed_date,buiness,admin,status)
		return json.dumps({'code':200})
	else:
		return json.dumps({'code':400,'error':error})


@app.route('/asset/delete/',methods=['get'])
def asset_delete():
	id =  request.args.get('id',0)
	id = int(str(id))
	print type(id)
	models.asset_delete(id)
	return json.dumps({'code':200})

#################### machine_room,add,delete,select,change ##################

@app.route('/machine_room/')
def get_machine_room():
	machine_room = models.get_machine_room()
	print machine_room
	return render_template('machine_room.html',machine_room = machine_room)  # machine_room是一个列表,列表中的每一项是一个字典


@app.route('/machine_room/add/')
def machine_room_add():
	return render_template('machine_room_add.html')


@app.route('/machine_room/save/', methods=['POST','GET'])
def machine_room_save():
	params = request.form if 'POST' == request.method else request.args
	print request.form
	return json.dumps({'abc':1})
	name = params.get('name','')
	addr = params.get('addr','')
	ip_ranges = params.get('ip_ranges','')
	ok,error = models.validate_machine_room_save(name,addr,ip_ranges)
	if ok:
		models.machine_room_save(name,addr,ip_ranges)
		return redirect('/machine_room/')
	else:
		return render_template('machine_room_add.html', error=error,name=name, addr=addr, ip_ranges=ip_ranges)


@app.route('/machine_room/save/json/', methods=['POST','GET'])
def machine_room_save_json():
	params = request.form if 'POST' == request.method else request.args
	name = params.get('name','')
	addr = params.get('addr','')
	ip_ranges = params.get('ip_ranges','')
	ok,error = models.validate_machine_room_save(name,addr,ip_ranges)
	if ok:
		models.machine_room_save(name,addr,ip_ranges)
		return json.dumps({'code':200})
	else:
		return json.dumps({'code':400,'error':error})


@app.route('/machine_room/view/', methods=['GET'])
def machine_room_view():
	id = request.args.get('id',0)						#通过将id传给models.get_machine_room_by_id函数获取机房信息
	machine_room = models.get_machine_room_by_id(id)	#machine_room是一个字典,包含机房的信息
	print machine_room
	return render_template('machine_room_view.html',id=machine_room['id'],name=machine_room['name'],addr=machine_room['addr'],\
							ip_ranges=machine_room['ip_ranges'])


@app.route('/machine_room/modify/', methods=['POST','GET'])
def machine_room_modify():
	params = request.form if 'POST' == request.method else request.args
	id = params.get('id',0)
	name = params.get('name','')
	addr = params.get('addr','')
	ip_ranges = params.get('ip_ranges','')
	# print '-' * 50 
	# print 'id   %s' % id
	# print 'name %s' % name
	# print 'addr %s'  % addr
	# print 'ip_ranges %s' % ip_ranges
	# print '-' * 50 
	ok,error = models.validate_machine_room_save(name,addr,ip_ranges)
	if ok:
		models.machine_room_modify(id,name,addr,ip_ranges)
		return redirect('/machine_room/')
	else:
		return render_template('machine_room_view.html',error=error,name=name,addr=addr,ip_ranges=ip_ranges)


@app.route('/machine_room/delete/',methods=['GET'])
def machine_room_delete():
	id = request.args.get('id',0)
	models.machine_room_delete(id)
	return redirect('/machine_room/')



#################### 主机监控 ##################
@app.route('/monitor/host/create/',methods=['POST'])
def monitor_host_create():
	models.monitor_host_create(request.form)
	return json.dumps({'code' : 200, 'result' : ''})




@app.route('/monitor/host/list/')
def monitor_host_list():
	asset = models.get_asset_by_id(request.args.get('id',0))
	ip = asset.get('ip','')
	result = models.monitor_host_list(ip)
	return json.dumps({'code' : 200, 'result' : result})
	# result = {
	# 	'categories' : ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun','Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'],
	# 	'series' : [{
	# 	    "name": 'CPU',
	# 	    "data": [7.0, 6.9, 9.5, 14.5, 18.2, 21.5, 25.2, 26.5, 23.3, 18.3, 13.9, 9.6]
	# 	}, {
	# 	    "name": u'内存',
	# 	    "data": [-0.2, 0.8, 5.7, 11.3, 17.0, 22.0, 24.8, 24.1, 20.1, 14.1, 8.6, 2.5]
	# 	}, {
	# 	    "name": u'磁盘',
	# 	    "data": [-0.9, 0.6, 3.5, 8.4, 13.5, 17.0, 18.6, 17.9, 14.3, 9.0, 3.9, 1.0]
	# 	}]
	# }

	return json.dumps({'code' : 200, 'result' : result})



#################### 日志 ##################
@app.route('/log/')
def log():
	if session.get('user') is None: return redirect('/')

	#logfile='/root/www.log'
	logfile = '/home/kk/class11/fangj/www.log'
	topn = request.args.get('topn',10)
	logs = models.get_topn(logfile,int(str(topn)))
	return render_template('log.html',log = logs)


if __name__ == '__main__':
	app.run(host='0.0.0.0',port=18989,debug=True)


