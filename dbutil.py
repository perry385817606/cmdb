#!/usr/bin/python
#encoding=utf8

import MySQLdb
import gconf

#增、删、改、查
def execute_sql(sql,args,is_fetch):
	rt_cnt = 0
	rt_list = []
	conn = MySQLdb.connect(host=gconf.MYSQL_HOST,\
							port=gconf.MYSQL_PORT,\
							user=gconf.MYSQL_USER,\
							passwd=gconf.MYSQL_PASSWD,\
							db=gconf.MYSQL_DB,\
							charset=gconf.MYSQL_CHARSET)
	cursor = conn.cursor()
	cursor.execute(sql,args)
	if is_fetch:
		rt_list = cursor.fetchall()
	else:
		conn.commit()

	cursor.close()
	conn.close()
	return rt_cnt,rt_list

if __name__ == "__main__":
	rt_cnt = 0
	rt_list = []
	SQL1 = 'SELECT * FROM user WHERE id < %s'
	SQL2 = 'UPDATE user SET name="test99" WHERE id = %s'
	SQL_MAX_ID = 'SELECT MAX(id) FROM user'
	maxid = execute_sql(SQL_MAX_ID,args=(),is_fetch=True)
	maxid=int(maxid[1][0][0])
	print maxid
	# print rt_cnt
	# print rt_list
	SQL_USER_VALIDATE_NAME= 'SELECT * FROM user WHERE id <= %s AND name = %s '
	rt = execute_sql(SQL_USER_VALIDATE_NAME,args=(maxid,'test66'),is_fetch=True)
	print rt[1]