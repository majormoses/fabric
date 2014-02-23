#!/usr/bin/python

# fabric libs
from fabric.api import *
from fabric.contrib.files import *
# useful standard lib to get passwords from prompt and not disaplay
import getpass
# useful sysytem commands
import os
import subprocess
import re
import commands
import time
import datetime

# global fallback user
env.user='ops'


# hosts should be single quoted and comma seperated
def all_internal_servers():
	env.hosts=['']

# centeral config server
def auth_host():
	env.hosts=['']
	env.user='root'

hosts should be single quoted and comma seperated
def xen_servers():
	env.user='root'
	env.hosts=['']

# never store pass in text will get later from prompt
ops_pass=''
ops_pass_confirm=''
admin_pass=''
admin_pass_confirm=''


# pings host and determines if live
def pingHost(ip):
	response = os.system("ping -c 1 " + ip)
	if response == 0:
#		ping is sucess, machine is live
		print "there is a live host on this ip address"
		confirm = raw_input('confirm you wish to proceed [y/n]: ')
#		retatard proof script (force user to confirm changes)
		while confirm != 'y':
			confirm = raw_input('confirm you wish to proceed [y/n]: ')
			print "confirm: ", confirm
	else:
		print "there is no live host on this ip address"


# will configure existing servers with ldap client packages/files to authenticate
def ldapClientConfig():
#	installs neccessary packages
	sudo('DEBCONF_FRONTEND="noninteractive" apt-get install -y libpam-ldap libnss-ldap nss-updatedb libnss-db')
#	rsync the config files from auth
	sudo('rsync -arvP root@CHANGE_THIS_SERVER_NAME_IP:/home/ops/shared-etc/ldap-client-files/etc/ /etc/')

# configures internal server for static IP and dns
# should be run like this: fab -f fab.py -H currentip configEth0:server_ip='desiredip'
def configEth0(server_ip):
#	overide defualt user
#	env.user='root'
#	get IP of server logged into
	oldIP = run('ifconfig eth0 | grep "inet addr:" | cut -d: -f2 | awk \'{ print $1}\'')
	run('whoami')
#	rsync the template file
	sudo('rsync -arvP root@CHANGE_THIS_SERVER_NAME_IP:/home/ops/shared-etc/network/interfaces /etc/network/interfaces')
#	check if host is alive
	print 'pinging ',server_ip
	pingHost(server_ip)
#	sed to replace IP
	sudo('sed -i "s|CHANGE_THIS_SERVER_NAME_IP|' + server_ip + '|g"'' /etc/network/interfaces')
	run('cat /etc/network/interfaces')
	confirm = raw_input('please confirm that ip output of network interfaces is good [y/n]: ')
#	fail count
	fail_count=0
#	while you did not confirm network configs are good
	while confirm != 'y':
		fail_count += 1
		new_ip=raw_input('You fool! your fail count is currently ' + str(fail_count) + '. Input desired ip or I shall taunt you again: ')
#		running sed with new IP
		sudo('sed -i "s|CHANGE_THIS_SERVER_NAME_IP|' + new_ip + '|g"'' /etc/network/interfaces')
		run('cat /etc/network/interfaces')
#		confirm working?
		confirm = raw_input('please confirm that ip output of network interfaces is good [y/n]: ')
	else:
		sudo('reboot')


# will rename servers to reflect their real name not using localhost OR ubuntu
def nameMyServer():
#	get ip of server
	server_ip = run('ifconfig eth0 | grep "inet addr:" | cut -d: -f2 | awk \'{ print $1}\'')
#	get old server name
	old_server_name = run('hostname')
#	get new server name
	print 'if you would not like to rename this host just hit enter'
	server_name = raw_input('what is the name of this server, my ip is: ' + server_ip +' : ')
#	if 0 you do not wish to rename
	if len(server_name) == 0:
		exit(0)
#	rename server
	else:
#		replaces old_hostname with new one in /etc/hostname
		sudo('sed -i "s|' + old_server_name + '|' + server_name + '|g"'' /etc/hostname')
#		replaces old_hostname with new one in /etsc/hosts
		if old_server_name == 'localhost':
			print 'tricky...'
			sudo('sed -i "s|127.0.0.1	' + old_server_name + '|127.0.0.1	' + server_name + '|g"'' /etc/hosts')
			sudo('sed -i 1i"127.0.0.1	localhost" /etc/hosts')
			sudo('hostname '+ server_name)
		else:
			sudo('sed -i "s|' + old_server_name + '|' + server_name + '|g"'' /etc/hosts')
			sudo('hostname ' + server_name)


# adds a users authorized key to each system / Needs to have pushed to auth manually
# should be run like this: fab -f fab.py syncUserKeys:user_id='useryouwishtosync'
def syncUserKeys(user_id):
#	get username
	env.user=user_id
	run('whoami')
#	checks if the homedir and .ssh folder exist
	if not exists('/home/'+ user_id + '/.ssh'):
		run('echo need to create homedir')
#		rsync the homedir ignoring host keys
		run('rsync -arvP -e "ssh -o StrictHostKeyChecking=no" CHANGE_THIS_SERVER_NAME_IP:~/ /home/' + user_id + '/')
	else:
#		already exists
		run('echo homedir and ssh already set up')


# pushes root ssh keys from SOME_HOST to each host
def syncRootKeys():
#	overide default user
	env.user='root'
	run('whoami')
# rsyncs roots ssh keys from auth
	run('rsync -arvP -e "ssh -o StrictHostKeyChecking=no" root@CHANGE_THIS_SERVER_NAME_IP:~/.ssh/ ~/.ssh/')


# deletes any local instance of ops user
def delLocalAdmin():
#	overide default user
	env.user='root'
	run('whoami')
#	checking existance
	if exists('/home/ops'):
#		blast away
		run('userdel ops')
		run('rm -Rf /home/ops')
	else:
		print 'these are not the droids you are looking for, move along...'


# pushes keys from ops@CHANGE_THIS_SERVER_NAME_IP to each machine
def syncOpsKeys():
	run('whoami')
#	confirm that homedir and ssh do not exist
	if not exists('/home/ops/.ssh/'):
#		create homedir and .ssh dir
		run('mkdir /home/ops/.ssh')
	else:
		print 'these are not the droids you are looking for, move along...'
#	rsync the .ssh dir / Ignores host keys
	sudo('rsync -arvP -e "ssh -o StrictHostKeyChecking=no" ops@CHANGE_THIS_SERVER_NAME_IP:/home/ops/.ssh/ /home/ops/.ssh/')
#	ensuring that perms/ownership is correct
	sudo('chown -R ops:ops /home/ops')
	sudo('chmod 700 /home/ops/.ssh/')
	sudo('chmod 600 /home/ops/.ssh/id_rsa')
	sudo('chmod 600 /home/ops/.ssh/id_rsa.pub')
	sudo('chmod 600 /home/ops/.ssh/authorized_keys')


# this is for creating a local admin
def addLocalAdmin():
#	overide default user
	env.user='root'
	run('whoami')
#	prompt for user
	admin_user = raw_input('enter username: ')
#	these are global to ensure they persist after each host is done
	global admin_pass
	global admin_pass_confirm
	if admin_user == 'ops':
		if exists('/home/ops/'):
			print 'ops exists not creating, will sync ops keys and exit'
			syncOpsKeys()
			exit(0)
	while len(admin_pass) >= 20:
#		defines function passPrompt (lambda) to get a password and a confirm password
		passPrompt = lambda: (getpass.getpass(), getpass.getpass('Retype password: '))
#		these vars restpectively get the input of the password you type
		print 'Passwords will not be visable!'
		admin_pass, admin_pass_confirm = passPrompt()
#		ensures the two passwords match
		while admin_pass != admin_pass_confirm:
			print 'You Fool! You must type the same pw twice!'
			admin_pass, admin_pass_confirm = passPrompt()
#			the password is now >= 20 chars and you have typed the same password twice
		else:
			print 'admin_user: ' + admin_user
			print 'admin_pass: ' + admin_pass
			print 'password has been saved correctly'
#		creates user in sudo group, bash shell, and no password
		sudo('useradd ' + admin_user + ' -G sudo -m -s /bin/bash')
#		uses chpasswd to 'create' a password with the password we captured earlier
		sudo('echo "%s:%s" | chpasswd' % (admin_user, admin_pass))


# creates backup dirs
def createBackUpDirs():
#	needs root
	env.user = 'root'
	env.key_filename = "/root/.ssh/id_rsa"
	hn = run('hostname')
#	gets dates for file/folder name
	year = datetime.date.today().strftime("%Y")
	month = datetime.date.today().strftime("%m")
	day = datetime.date.today().strftime("%d")
#	get sr uuid
	sr_uuid = run('xe sr-list tags=backup-sr | grep uuid | cut -f2 -d":" | tr -d [:blank:]')
#	check if dir exists
	if not exists('/var/run/sr-mount/' + str(sr_uuid) + '/' +  year + '/'  + month +  '-'  + day + '/' ):
		run('mkdir -p /var/run/sr-mount/' + sr_uuid + '/' + year + '/' + month + '-' + day +'/' )
		print 'created folder for today'
	else:
		print 'back dir for today already exists, move along'
#	ensures we start with a fresh log each time
	run('cat /dev/null > /var/run/sr-mount/' + sr_uuid + '/' + year + '/' + month + '-' + day +'/backup.log' )


# function gets list of VM's
def getListOfVMs():
#	need to run as root
	env.user='root'
	env.key_filename = "/root/.ssh/id_rsa"
#	get hostname
	xs = run('hostname')
	print xs
#	base xen list command
	xe_list = 'xe vm-list is-control-domain=false is-a-snapshot=false'
#	awk statement to get the xs_name (name of the server according to xen) and uuid
	awk_state = 'awk \'{if ( $0 ~ /uuid/) {uuid=$5} if ($0 ~ /name-label/) {$1=$2=$3="";vmname=$0; printf "%s:%s\\n", vmname, uuid}}\''
#	sed statement gets rid of whitespace
	sed_state = 'sed -e "s/^[ \t]*//"'
#	this is the command run to get a list of xen hosts located on the xen server,
#	it will create a file: list-of-vms-to-back-up.txt and it will be formateed
#	as xs_name:uuid
	list_vm_cmd = run('' + xe_list +' | '+ awk_state + ' | ' + sed_state + ' > list-vms-backup.txt')
	list_of_uuid = run('awk -F":" \'{ print $2 }\' list-vms-backup.txt > list-vm-uuids-backup.txt')
	list_of_names = run('awk -F":" \'{ print $1 }\' list-vms-backup.txt > list-vm-names-backup.txt')
#	list_of_names = run('awk -F":" \'{ print $1 }\' list-vms-backup.txt | tr -d [:blank:] > list-vm-names-backup.txt')
	run('rsync -arvP list-*.* root@10.160.2.100:/xs-backup-lists/' + xs + '/' )


# function to back uo a single VM
def backUpVM(uuid, xs_name):
#	need to run as root
	env.user='root'
	env.key_filename = "/root/.ssh/id_rsa"
	today = str(datetime.date.today())
#	determine start time
	stime = time.time()
#	cast variables as strings to protect from spaces
	uuid = str(uuid)
	xs_name = re.escape(str(xs_name))
#	dates for file names
#	gets dates for file/folder name
	year = datetime.date.today().strftime("%Y")
	month = datetime.date.today().strftime("%m")
	day = datetime.date.today().strftime("%d")
#	gets the sr base path
	sr_base = '/var/run/sr-mount'
	sr_uuid = str(run('xe sr-list tags=backup-sr | grep uuid | cut -f2 -d":" | tr -d [:blank:]'))
	filename =  str(sr_base + '/' + sr_uuid + '/'+ year + '/' + month + '-' + day + '/' + xs_name +  ".xva")
	#this ejects any cd
	dvdstate = run('xe vm-cd-list uuid='+ uuid + ' | grep "empty ( RO)" | awk \'{print $4}\'')
	if dvdstate == "false":
		print 'removing any cd\'s from: ', xs_name
		run('xe vm-cd-eject vm=' + xs_name)
	#this deletes existsing backup if named same
	print 'filename: ', filename
	print 'running initial snapshot'
#	this command creates a snapshot
	backup_vm_cmd = run('xe vm-snapshot uuid=' + uuid + ' new-name-label=' + xs_name + '-' + today)
	snapshot_uuid = str(commands.getoutput(backup_vm_cmd).replace("sh: 1: ","").replace(": not found",""))
	print 'done creating snapshot: ', snapshot_uuid
#	this command sets HA to NAY for template
	print 'setting template for HA to NAY'
	backup_vm_cmd = 'xe template-param-set is-a-template=false ha-always-run=false uuid=' + snapshot_uuid
	commands.getoutput(backup_vm_cmd)
	print 'done creating template'
#	this exports the template we created as a cloned
	print 'exports template to a cloned vm'
	print 'checking if ' + filename + 'exists'
#	delete any lingering copies
	run('rm -f ' + filename)
#	back up the vm
	backup_vm_cmd = run('xe vm-export vm=' + snapshot_uuid + ' filename=' + filename)
	commands.getoutput(backup_vm_cmd)
	print 'done creating clone'
	run('chmod 660 '+filename)
	etime = time.time()
	ttime = (etime - stime)
	run('echo ' + filename + '-'  + str(ttime) + ' >> ' + sr_base + '/' + sr_uuid + '/' + year + '/' + month + '-' + day + '/backup.log')
	#removing old snapshot
	run('xe snapshot-uninstall snapshot-uuid=' + snapshot_uuid + ' force=true')
	print 'does this still exist? ', snapshot_uuid


# function to backup all vms returned by getOfListofVMs()
def backUpAllVMs():
#	will run as root if using -H xen_servers
	env.user='root'
	env.key_filename = "/root/.ssh/id_rsa"
#	gets hostname of xs (label)
	xs = run('hostname')
#	makes sure that dir for today exists
	createBackUpDirs()
#	gets the list of vm
	getListOfVMs()
#	initialize arrays
	uuids = []
	names = []
#	open files and get them into arrays
	uuids = open('/xs-backup-lists/' + xs + '/list-vm-uuids-backup.txt').read().splitlines()
	names = open('/xs-backup-lists/' + xs + '/list-vm-names-backup.txt').read().splitlines()
#	resets count
	count = 0
#	for every uuid in uuids file
	for u in range(0, len(uuids) -1):
		count +=1
#		backup the vm passing the uuid and xen label/name
		print 'uuid: ', uuids[count]
		print 'name: ', names[count]
		backUpVM(uuids[count],names[count])
	print 'all uuids: ', uuids
	print 'all names: ', names
	rotateBackUps()


	# rotates backups
def rotateBackUps():
	env.user = 'root'
#	gets the sr
	sr_base = '/var/run/sr-mount'
	sr_uuid = run('xe sr-list tags=backup-sr | grep uuid | cut -f2 -d":" | tr -d [:blank:]')
	sr_path = sr_base + '/' + sr_uuid
#	date stuff
	year = datetime.date.today().strftime("%Y")
#	this will get the dat in 'month day_of_month' format for files
	file_date_cmd = run("ls -lt | awk '{print $6,$7}'")
#	getting dates in same format
	today = run('date +"%b %d"')
	# mtime +1 is GREATER than 1 day.
	remove_empty_dir = run('find ' + sr_path + '/' + year + '/' + ' -type d -empty -delete')
	two_days_ago = run('find ' + sr_path + '/' + year + '/' + ' -type f -not -name "*.gz" -mtime +1 -exec gzip {} \;')
	eight_days_ago = run('find ' + sr_path + '/' + year + '/' + ' -mtime +1 -mtime -8 -delete')
	remove_empty_dir = run('find ' + sr_path + '/' + year + '/' + ' -type d -empty -delete')
	print 'today: ', today
	print 'two days ago: ', two_days_ago
	print 'eight days ago: ', eight_days_ago




