import mysql.connector
import os
import re
import time
import threading
from pexpect import pxssh


def read_file(filename):
	list_ip=[]
	with open(filename) as f:
		for i in f.read().split('\n'):
			if '#' not in i:
				list_ip.append(i.strip())
	return list_ip

def write_file(content):
	f=open('missing.txt','a')
	f.write(content)
	f.close()

def get_previour_miss():
	list_=[]
	# print 1
	try:
		with open ('missing.txt') as f:
			for i in f.read().split('\n'):
				list_.append(i.strip())
		os.system('rm -rf missing.txt')
		# print list_
		return list_
	except:
		return []
def convert_ascii(string_):
	ansi_escape = re.compile(r'''
	    \x1B    # ESC
	    [@-_]   # 7-bit C1 Fe
	    [0-?]*  # Parameter bytes
	    [ -/]*  # Intermediate bytes
	    [@-~]   # Final byte
	''', re.VERBOSE)
	result = ansi_escape.sub('', string_)
	return result

def returnNotMatches(a, b):
    return [x for x in b if x not in a]

def ssh_check_missing_live(j,s,p):
	list_conf_edge = []
	list_vcl_edge = []
	cmd_vcl = 'ls /etc/varnish/conf.d/ | sed -e \'s/.vcl//g\''
	cmd_conf = 'ls /usr/local/nginx-1.10.1/conf/sites-enabled/ | sed -e \'s/.conf//g\''

	s.sendline(cmd_conf)
	s.prompt()
	for i in s.before.strip().split('\r\n'):
		if 'ls ' not in i:
			list_conf_edge.append(i)
	for i in returnNotMatches(list_conf_edge, ID_live_conf[0]):
		if i+'.conf' in p:
			write_list[j].append(i + '.conf')
			write_file(i+'.conf')
		else:
			write_file(i + '.conf')

	s.sendline(cmd_vcl)
	s.prompt()
	for i in s.before.strip().split('\r\n'):
		if 'ls ' not in i:
			list_vcl_edge.append(i)
	for i in returnNotMatches(list_vcl_edge, ID_live_conf[1]):
		if i + '.vcl' in p:
			write_list[j].append(i + '.vcl')
			write_file(i + '.vcl\n')
		else:
			write_file(i + '.vcl\n')

def ssh_check_missing_vod(j,s,p):
	list_conf_edge = []
	cmd_vod = 'ls /usr/local/nginx-1.10.1/conf/sites-enabled/ | sed -e \'s/.conf//g\''
	s.sendline(cmd_vod)
	s.prompt()
	for i in s.before.strip().split('\r\n'):
		if 'ls ' not in i:
			list_conf_edge.append(i)
	for i in returnNotMatches(list_conf_edge, ID_vod_conf):
		if i + '.conf' in p:
			write_list[j].append(i + '.conf')
			write_file(i + '.conf\n')
		else:
			write_file(i + '.conf\n')

def sql_query(cmd):
	cnx = mysql.connector.connect(user='viethd_monitor', password='xxx', host='x.x.x.x', database='cdn_portal')
	cursor = cnx.cursor(buffered=True)
	cursor.execute(cmd)
	output=cursor.fetchall()
	cursor.close()
	cnx.close()
	return output

def get_list_live():
	cmd_vcl="""SELECT a.id FROM vgcdn_resource AS a JOIN `vgcdn_domain_routing` AS b ON a.`domain_routing_id` = b.`id`
	WHERE a.status NOT IN (2,9,10) AND b.`resource_type_id` = 1 AND a.changed_on >= DATE_SUB(NOW(), INTERVAL 90 DAY)"""

	cmd_conf="""SELECT a.id FROM vgcdn_resource AS a 
	JOIN `vgcdn_domain_routing` AS b ON a.`domain_routing_id` = b.`id` 
	JOIN `vgcdn_static_features` AS c ON a.id = c.resource_id
	WHERE a.status NOT IN (2,9,10) AND b.`resource_type_id` = 1 AND c.protocol LIKE '%SSL%' AND a.changed_on >= DATE_SUB(NOW(), INTERVAL 90 DAY)"""
	list_id_conf=[]
	list_id_vcl=[]

	output_conf=sql_query(cmd_conf)
	output_vcl=sql_query(cmd_vcl)
	for i in output_conf:
		list_id_conf.append(str(i[0]))
	for i in output_vcl:
		list_id_vcl.append(str(i[0]))
	list_id_conf.append('id1')
	# list_id_vcl.append('id2')
	return (list_id_conf,list_id_vcl)

def get_list_vod():
	cmd_vod="""SELECT a.id FROM vgcdn_resource AS a JOIN `vgcdn_domain_routing` AS b ON a.`domain_routing_id` = b.`id` 
	WHERE a.status NOT IN (2,9,10) AND b.`resource_type_id` = 2 AND a.changed_on >= DATE_SUB(NOW(), INTERVAL 90 DAY)"""
	list_id_vod=[]
	output=sql_query(cmd_vod)
	for i in output:
		list_id_vod.append(str(i[0]))
	list_id_vod.append('id3')
	return list_id_vod

class send(threading.Thread):
	def __init__(self, ip_, mode, previour_miss):
		threading.Thread.__init__(self)
		self.ip_=ip_
		self.mode=mode
		self.previour_miss=previour_miss
	def run(self): ## bat buoc la run
		try:
			s = pxssh.pxssh(timeout=10)
			s.login(self.ip_, '****', '******', auto_prompt_reset=True)
		except:
			write_list[self.ip_]=['SSH timeout',]
			return

		if self.ip_ not in write_list:
			write_list[self.ip_] = []
		if  self.mode == 'all':
			ssh_check_missing_live(self.ip_,s,self.previour_miss)
			ssh_check_missing_vod(self.ip_,s,self.previour_miss)
		elif self.mode == 'live':
			ssh_check_missing_live(self.ip_,s,self.previour_miss)
		else:
			ssh_check_missing_vod(self.ip_,s,self.previour_miss)
		s.logout()

if __name__ == '__main__':
	start_ = time.time()
	threads=[]
	write_list = {}
	PI_live=read_file('list.live')
	PI_vod=read_file('list.vod')
	ID_live_conf=get_list_live()
	ID_vod_conf=get_list_vod()
	previour_miss = get_previour_miss()
	for j in set(PI_live+PI_vod):
		if j in PI_live and j in PI_vod :
			thread = send(j, 'all', previour_miss)
		elif j in PI_live:
			thread = send(j, 'live', previour_miss)
		else:
			thread = send(j, 'vod', previour_miss)
		thread.start()
		threads.append(thread)
	for thread in threads:
		thread.join()
		threads = []
	# print write_list
	# print time.time()-start_
	########## OUTPUT ##########
	no_output=True
	for j in write_list:
		if write_list[j]!=[]:
			no_output=False
			break
	wf=''
	if no_output == False:
		wf = 'Host='
		print '2 CDN_missing_conf - CRIT (More)\\\\n ',
		for i in write_list:
			print write_list[i]
			if write_list[i]!=[]:
				# print '%s %s\\\\n'%(i,write_list[i]),
				wf=wf+'%s missing: %s |'%(i,write_list[i])
	else:
		print '0 CDN_missing_conf - OK'
	os.system('echo %s > missing2.txt'%wf)
