#!/usr/bin/python27
#encoding=utf-8

import json
import datetime
import MySQLdb
import gconf
import dbutil
def get_user():

	SQL_GET_USERS = 'SELECT id,name,password,age,department,sex,hobby,detail,homepage,birthday,email FROM user'

	rt_cnt,rt_list = dbutil.execute_sql(SQL_GET_USERS,(),True)
	columns = ('id','name','password','age','department','sex','hobby','detail','homepage','birthday','email')
	#return [dict(zip(columns,line)) for line in rt_list] #[{'id':1,'name':'pc','password':'123456','age':32},{'id':1,'name':'pc','password':'123456','age':32}]

	users = []
	for line in rt_list:
		user = dict(zip(columns,line))
		if user['birthday']:
			user['birthday'] = user['birthday'].strftime('%Y-%m-%d')
		users.append(user)
	return users


def get_user_by_id(uid):

	SQL_USER_BY_ID_COLUMNS = ('id','name','age','department','sex','hobby','detail','homepage','birthday','email')
	SQL_USER_BY_ID = 'SELECT id,name,age,department,sex,hobby,detail,homepage,birthday,email FROM user WHERE id=%s'

	rt_cnt,rt_list = dbutil.execute_sql(SQL_USER_BY_ID,(uid,),True) #rt是fetchall()的结果,是元组嵌套元组((),())
																			 #rt[0]相当于元组中第一个元素即()
	# return {} if rt_list is None else dict(zip(SQL_USER_BY_ID_COLUMNS,rt_list[0]))
	users = []
	for line in rt_list:
		user = dict(zip(SQL_USER_BY_ID_COLUMNS,line))
		if user['birthday']:
			user['birthday'] = user['birthday'].strftime('%Y-%m-%d')
		users.append(user)
	return users[0] if users else {}


def user_save(username,age,password,department,sex,hobby,detail,homepage,birthday,email):
	SQL_ADD_USER = 'INSERT INTO user(name,age,password,department,sex,hobby,detail,homepage,birthday,email) VALUES(%s,%s,md5(%s),%s,%s,%s,%s,%s,%s,%s)'

	hobby = str(','.join(hobby))
	DEP = {'1':'研发部门','2':'测试部门','3':'运维部门'}
	SEX = {'1':'男','0':'女'}
	department = DEP.get(department,None)
	sex = SEX.get(sex,None)
	COLUMNS = (username,age,password,department,sex,hobby,detail,homepage,birthday,email)
	dbutil.execute_sql(SQL_ADD_USER ,COLUMNS,False)
	return True


def validate_login(username,password):
	SQL_VALIDATE_LOGIN = 'SELECT id,name FROM user WHERE name = %s AND password= md5(%s)'

	rt_cnt,rt = dbutil.execute_sql(SQL_VALIDATE_LOGIN,(username,password),True)

	columns = ('id','name')
	return None if rt is None else dict(zip(columns,rt[0]))


def validate_user_save(username,age,password):
	if username.strip() == '':
		return False,'username is empty'
	if len(username.strip()) > 25:
		return False,'username is gt 25'
	if password.strip() == '':
		return False,'password is empty'
	if len(password.strip()) < 6 or len(password.strip()) > 25:
		return False,'password length between 6 and 25'

	if not str(age).isdigit() or int(age) < 1 or int(age) > 100:
		return False, 'age is not a between 1 and 100 integer'

	#检查用户名是否重复，不允许重名, 判断依据:查询已有用户名中是否已有相同的用户名
	SQL_USER_VALIDATE_NAME= 'SELECT * FROM user WHERE id <= %s AND name = %s '
	SQL_MAX_ID = 'SELECT MAX(id) FROM user'
	# conn = MySQLdb.connect(host=gconf.MYSQL_HOST,\
	# 						port=gconf.MYSQL_PORT,\
	# 						user=gconf.MYSQL_USER,\
	# 						passwd=gconf.MYSQL_PASSWD,\
	# 						db=gconf.MYSQL_DB,\
	# 						charset=gconf.MYSQL_CHARSET)
	# cursor = conn.cursor()
	# cursor.execute(SQL_MAX_ID)
	# maxid = cursor.fetchone()
	# maxid = int(maxid[0])
	# cursor.execute(SQL_USER_VALIDATE_NAME,(maxid,username))
	# rt = cursor.fetchone()

	# cursor.close()
	# conn.close()
	rt_cnt,maxid = dbutil.execute_sql(SQL_MAX_ID,(),True)
	maxid = int(maxid[0][0])
	rt_cnt,rt = dbutil.execute_sql(SQL_USER_VALIDATE_NAME,(maxid,username),True)

	if rt:
		return False,'The same username' 

	return True,''
	return True,''



def validate_user_modify(uid,username,age,detail,homepage,email):
	if not get_user_by_id(uid):
		return False,'user not found'
	if username.strip() == '':
		return False,'username is empty'
	if len(username.strip()) > 25:
		return False,'username is gt 25'
	if not str(age).isdigit() or int(age) < 1 or int(age) > 100:
		return False, 'age is not a between 1 and 100 integer'
	if  detail.strip() == '':
		return False,'简介为空'
	if homepage.strip() == '':
		return False,'主页为空'
	if email.strip() == '':
		return False,'电子邮箱为空'


	#检查用户名是否重复，不允许重名, 判断依据:id不是自身，name相同的即为重名
	SQL_USER_VALIDATE_NAME= 'SELECT * FROM user WHERE id != %s AND name = %s '

	rt_cnt,rt = dbutil.execute_sql(SQL_USER_VALIDATE_NAME,(uid,username),True)
	if rt:
		return False,'The same username' 

	return True,''


def user_modify(uid,username,age,department,sex,hobby,detail,homepage,birthday,email):
	DEP = {'1':'研发部门','2':'测试部门','3':'运维部门'}
	SEX = {'1':'男','0':'女'}
	department = DEP.get(department,None)
	sex = SEX.get(sex,None)
	hobby = str(','.join(hobby))   #列表要先转换成字符串再插入到数据库中

	SQL_USER_MODIFY = 'UPDATE user SET name=%s,age=%s,department=%s,sex=%s,hobby=%s,detail=%s,homepage=%s,birthday=%s,email=%s WHERE id=%s'
	COLUMNS = (username,age,department,sex,hobby,detail,homepage,birthday,email,uid)
	dbutil.execute_sql(SQL_USER_MODIFY,COLUMNS,False)
	return True


def user_delete(uid):
	if not get_user_by_id(uid):
		return False,'user not found'

	SQL_USER_DELETE = 'DELETE FROM user WHERE id = %s'
	dbutil.execute_sql(SQL_USER_DELETE,(uid,),False)
	return True,''


#################### assets,add,delete,select,change ##################
def get_assets():
	SQL_ASSET_LIST_COLUMNS = 'id,sn,hostname,os,ip,machine_room_id,vendor,model,ram,cpu,disk,time_on_shelves,over_guaranteed_date,buiness,admin,status'.split(',')
	SQL_ASSET_LIST = 'select id,sn,hostname,os,ip,machine_room_id,vendor,model,ram,cpu,disk,time_on_shelves,over_guaranteed_date,buiness,admin,status from asset where status!=2;'
	rt_cnt,rt_list = dbutil.execute_sql(SQL_ASSET_LIST,(),True)
	#print rt_list
	assets = []
	for rt in rt_list:
		asset = dict(zip(SQL_ASSET_LIST_COLUMNS,rt))
		for key in 'time_on_shelves,over_guaranteed_date'.split(','):
			if asset[key]:
				asset[key] = asset[key].strftime('%Y-%m-%d')
		assets.append(asset)
	return assets

	#return [dict(zip(SQL_ASSET_LIST_COLUMNS,rt)) for rt in rt_list] #TypeError: datetime.date(2016, 11, 16) is not JSON serializable

def get_asset_by_id(aid):
	SQL_ASSET_LIST_BY_ID = 'select id,sn,hostname,os,ip,machine_room_id,vendor,model,ram,cpu,disk,time_on_shelves,over_guaranteed_date,buiness,admin,status from asset where status!=2 and id=%s;'
	SQL_ASSET_LIST_COLUMNS = 'id,sn,hostname,os,ip,machine_room_id,vendor,model,ram,cpu,disk,time_on_shelves,over_guaranteed_date,buiness,admin,status'.split(',')
	rt_cnt,rt_list = dbutil.execute_sql(SQL_ASSET_LIST_BY_ID,(aid,),True)
	#print rt_list
	assets = []
	for rt in rt_list:
		asset = dict(zip(SQL_ASSET_LIST_COLUMNS,rt))
		for key in 'time_on_shelves,over_guaranteed_date'.split(','):
			if asset[key]:
				asset[key] = asset[key].strftime('%Y-%m-%d')
		assets.append(asset)
	return assets[0] if assets else {}


def validate_asset_save(req):
	return True,''
	#return False,'sn is empty'

def asset_save(sn,hostname,ip,os,machine_room_id,vendor,model,ram,cpu,disk,time_on_shelves,over_guaranteed_date,buiness,admin,status):
	# machine_room_id = int(machine_room_id)
	# cpu = int(cpu)
	# ram = int(ram)
	# disk = int(disk)
	# time_on_shelves = str(time_on_shelves)
	# over_guaranteed_date = str(over_guaranteed_date)
	# SQL_ASSET_SAVE = 'INSERT INTO asset (sn,hostname,ip,os,machine_room_id,vendor,model,ram,cpu,disk,time_on_shelves,over_guaranteed_date,buiness,admin,status) VALUES("%s","%s","%s","%s","%s","%s","%s","%s","%s","%s","%s","%s","%s","%s","%s");'
	# SQL_ASSET_SAVE_COLUMNS = (sn,hostname,ip,os,machine_room_id,vendor,model,ram,cpu,disk,time_on_shelves,over_guaranteed_date,buiness,admin,status)
	# dbutil.execute_sql(SQL_ASSET_SAVE,SQL_ASSET_SAVE_COLUMNS,False)
	return True


def asset_delete(id):
	DELETE_ASSET_BY_ID_SQL = 'update asset set status=2 where id=%s'
	dbutil.execute_sql(DELETE_ASSET_BY_ID_SQL,(id,),False)
	return True

#################### machine_room,add,delete,select,change ##################
def get_machine_room():
	GET_MACHINE_ROOM_SQL = 'SELECT id,name,addr,ip_ranges FROM machine_room'
	
	rt_cnt,rt_list = dbutil.execute_sql(GET_MACHINE_ROOM_SQL,(),True)

	"""
	#返回值machine_room是一个列表，列表中的每个元素是一个字典,{'id':1,'name':'xxxx','addr':'yyyy','ip_ranges':'zzzz'}
	#这里掌握zip、dict函数及列表生成式的用法,让代码更简洁
	#方法一:
	machine_room = []
	for line in rt:
		machine_room.append({'id': line[0], 'name': line[1], 'addr': line[2],'ip_ranges': line[3]})
	return machine_room
	"""

	"""
	#方法二：
	return [{'id': line[0], 'name': line[1], 'addr': line[2],'ip_ranges': line[3]} for line in rt]
	"""

	#方法三:
	columns = ('id','name','addr','ip_ranges')
	return [dict(zip(columns,rt)) for rt in rt_list]

def validate_machine_room_save(name,addr,ip_ranges):
	if name.strip() == '':
		return False,'机房名称为空'
	if addr.strip() == '':
		return False,'机房地址为空'
	if ip_ranges.strip() == '':
		return False,'IP网段为空'

	return True,''


def machine_room_save(name,addr,ip_ranges):
	SQL_MACHINE_ROOM_SAVE = 'INSERT INTO machine_room (name,addr,ip_ranges) VALUES (%s,%s,%s)'
	conn = MySQLdb.connect(host=gconf.MYSQL_HOST,\
							port=gconf.MYSQL_PORT,\
							user=gconf.MYSQL_USER,\
							passwd=gconf.MYSQL_PASSWD,\
							db=gconf.MYSQL_DB,\
							charset=gconf.MYSQL_CHARSET)
	cursor = conn.cursor()
	cursor.execute(SQL_MACHINE_ROOM_SAVE,(name,addr,ip_ranges))
	conn.commit()
	cursor.close()
	conn.close()


def get_machine_room_by_id(id):
	SQL_MACHINE_ROOM_BY_ID_COLUMS = ('id','name','addr','ip_ranges')
	SQL_GET_MACHINE_ROOM_BY_ID = 'SELECT id,name,addr,ip_ranges FROM machine_room'
	conn = MySQLdb.connect(host=gconf.MYSQL_HOST,\
							port=gconf.MYSQL_PORT,\
							user=gconf.MYSQL_USER,\
							passwd=gconf.MYSQL_PASSWD,\
							db=gconf.MYSQL_DB,\
							charset=gconf.MYSQL_CHARSET)
	cursor = conn.cursor()
	cursor.execute(SQL_GET_MACHINE_ROOM_BY_ID)
	rt = cursor.fetchone()
	cursor.close()
	conn.close()

	return {} if rt is None else dict(zip(SQL_MACHINE_ROOM_BY_ID_COLUMS,rt))

def machine_room_modify(id,name,addr,ip_ranges):
	SQL_MACHINE_ROOM_MODIFY = 'UPDATE machine_room SET name=%s,addr=%s,ip_ranges=%s WHERE id=%s'
	conn = MySQLdb.connect(host=gconf.MYSQL_HOST,\
							port=gconf.MYSQL_PORT,\
							user=gconf.MYSQL_USER,\
							passwd=gconf.MYSQL_PASSWD,\
							db=gconf.MYSQL_DB,\
							charset=gconf.MYSQL_CHARSET)
	cursor = conn.cursor()
	cursor.execute(SQL_MACHINE_ROOM_MODIFY,(name,addr,ip_ranges,id))
	conn.commit()
	cursor.close()
	conn.close()
	return True


def machine_room_delete(id):
	SQL_MACHINE_ROOM_DELETE = 'DELETE FROM machine_room WHERE id=%s'
	conn = MySQLdb.connect(host=gconf.MYSQL_HOST,\
							port=gconf.MYSQL_PORT,\
							user=gconf.MYSQL_USER,\
							passwd=gconf.MYSQL_PASSWD,\
							db=gconf.MYSQL_DB,\
							charset=gconf.MYSQL_CHARSET)
	cursor = conn.cursor()
	cursor.execute(SQL_MACHINE_ROOM_DELETE,args=(id,))
	conn.commit()
	cursor.close()
	conn.close()


#################### 主机监控 ##################
def monitor_host_create(req):
	SQL_MONITOR_HOST_CREATE = 'INSERT INTO monitor_host (ip,mem,cpu,disk,m_time,r_time) VALUES(%s,%s,%s,%s,%s,%s)'
	values = []
	for key in ['ip','mem','cpu','disk','m_time']:
		values.append(req.get(key,''))
		
	values.append(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
	dbutil.execute_sql(SQL_MONITOR_HOST_CREATE,values,False)



def monitor_host_list(ip):

	MONITOR_DATA_SQL = 'SELECT m_time,cpu,mem,disk FROM monitor_host WHERE ip=%s ORDER BY m_time ASC;'
	rt_cnt,rt_list = dbutil.execute_sql(MONITOR_DATA_SQL,(ip,),True)
	categoy_list = []
	cpu_list = []
	disk_list = []
	mem_list = []
	for line in rt_list:
		categoy_list.append(line[0].strftime('%Y-%m-%d %H:%M'))
		cpu_list.append(line[1])
		mem_list.append(line[2])
		disk_list.append(line[3])
	return {
		'categories' : categoy_list,
		'series' : [{
		    "name": 'CPU',
		    "data": cpu_list
		}, {
		    "name": u'内存',
		    "data": mem_list
		}, {
		    "name": u'磁盘',
		    "data": disk_list
		}]
	}

	# return {
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

#################### 日志 ##################
def get_topn(src,topn):
	key = []
	stat_dict = {}
	with open(src,'r') as fhandler:
		for line in fhandler:
			line_list = line.strip().split()
			key = line_list[0],line_list[6],line_list[8]
			stat_dict[key] = stat_dict.setdefault(key,0) + 1

	result= sorted(stat_dict.items(),key=lambda x:x[1])
	return result[-1:-topn - 1:-1]


if __name__ == '__main__':
	#src = '/root/www.log'
	#print get_topn(src,10)
	# print get_user()
	print get_user_by_id(43)


