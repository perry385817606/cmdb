#!/usr/bin/env python
#coding:utf8
#author:Allentuns
#time:2015-02-14
 
from subprocess import Popen,PIPE
import urllib,urllib2
import pickle
import json
import re
 
###[hostname message]#####
def get_HostnameInfo(file):
    with open(file,'r') as fd:
        data = fd.read().split('\n')
        for line in data:
            if line.startswith('HOSTNAME'):
                hostname = line.split('=')[1]
                break
    return hostname
 
#####[ipaddr message]#####
def get_Ipaddr():
    P = Popen(['ifconfig'],stdout=PIPE)
    data = P.stdout.read()
    list = []
    str = ''
    option = False
    lines = data.split('\n')
    for line in lines:
        if not line.startswith(' '):
            list.append(str)
            str = line
        else:
            str += line
    while True:
        if '' in list:
            list.remove('')
        else:
            break
    r_devname = re.compile('(eth\d*|lo)') 
    r_mac = re.compile('HWaddr\s([A-F0-9:]{17})')
    r_ip = re.compile('addr:([\d.]{7,15})')
    for line in list:
        devname = r_devname.findall(line)
        mac = r_mac.findall(line)
        ip = r_ip.findall(line)
        if mac:
            return  ip[0]
 
#####[osversion message]#####
def get_OsVerion(file):
    with open(file) as fd:
        lines = fd.readlines()
        os_version = lines[0][:-8]
    return os_version
 
#####[memory message]#####
def get_MemoryInfo(file):
   with open(file) as fd:
        data_list = fd.read().split('\n')
        MemTotal_line = data_list[0]
        Memory_K = MemTotal_line.split()[1]
        Memory_G = float(Memory_K)/1000/1000
        Memory_G2 = '%.2f' % Memory_G
        memory = Memory_G2 + 'G'
        return memory
 
#####[disk message]#####
def get_DiskInfo():
    p = Popen(['fdisk','-l'],stdout=PIPE,stderr=PIPE)
    stdout,stderr = p.communicate()
    diskdata = stdout
 
    disk_initial_size = 0
    re_disk_type = re.compile(r'Disk /dev/[shd]{1}.*:\s+[\d.\s\w]*,\s+([\d]+).*')
    disk_size_bytes = re_disk_type.findall(diskdata)
    for size in disk_size_bytes:
        disk_initial_size += int(size)
        disk_size_total_bytes = '%.2f'  % (float(disk_initial_size)/1000/1000/1000)
        disk_size_total_G = disk_size_total_bytes + 'G'
        disk = disk_size_total_G
    return disk
 
#####[cpu message]#####
def get_CpuInfo():
    p = Popen(['cat','/proc/cpuinfo'],stdout=PIPE,stderr=PIPE)
    stdout, stderr = p.communicate()
    cpudata = stdout.strip()
 
    cpu_dict = {}
    re_cpu_cores = re.compile(r'processor\s+:\s+([\d])')
    re_vendor_id = re.compile(r'vendor_id\s+:\s([\w]+)')
    re_model_name = re.compile(r'model name\s+:\s+(.*)')
 
    res_cpu_cores = re_cpu_cores.findall(cpudata)
    cpu_dict['Cpu_Cores'] = int(res_cpu_cores[-1]) + 1
    res_vendor_id = re_vendor_id.findall(cpudata)
    cpu_dict['Vendor_Id'] = res_vendor_id[-1]
    res_model_name = re_model_name.findall(cpudata)
    cpu_dict['Model_Name'] = res_model_name[-1]
    return cpu_dict
 
#####[Demi message]#####
def get_dmidecode():
    P = Popen(['dmidecode'],stdout=PIPE)
    data = P.stdout.read()
    lines = data.split('\n\n')
    dmidecode_line =  lines[2]    
    line = [i.strip() for i in dmidecode_line.split('\n') if i]
    Manufacturer = line[2].split(': ')[-1]
    product = line[3].split(': ')[-1]
    sn = line[5].split(': ')[-1]
    return Manufacturer,product,sn
 
if __name__ == '__main__':
    #####[get data]#####
    hostname = get_HostnameInfo('/etc/sysconfig/network')
    ip = get_Ipaddr()
    osversion = get_OsVerion('/etc/issue')
    memory = get_MemoryInfo('/proc/meminfo')
    disk = get_DiskInfo()
    Vendor_Id = get_CpuInfo()['Vendor_Id']
    Model_Name = get_CpuInfo()['Model_Name']
    Cpu_Cores = get_CpuInfo()['Cpu_Cores']
    Manufacturer,product,sn = get_dmidecode()
     
    #####[get dict]##### 
    hostinfo = {
    'hostname':hostname,
    'ip':ip,
    'osversion':osversion,
    'memory':memory,
    'disk':disk,
    'vendor_id':Vendor_Id,
    'model_name':Model_Name,
    'cpu_core':Cpu_Cores,
    'product':product,
    'Manufacturer':Manufacturer,
    'sn':sn,
    }
 
    print hostinfo
    #data = urllib.urlencode(hostinfo)
    #req = urllib2.urlopen('http://192.168.100.241:8000/hostinfo',data)
