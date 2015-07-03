#!/usr/bin/python

# Author: fan.zhiwei@qq.com
# purpose: auto create zookeeper cluster on auto-created EC2 instances
# Jul 2015
conf='ansible.cfg'
import sys
import os
import datetime
import time
import boto3

pid=os.getpid()
#read configure file content
cfgfile=open(conf, 'r')
content = cfgfile.read()
items = content.split("\n") 
configs={}
for item in items:
	item=item.strip()
	if item=='':
		continue
	keyvalue=item.split('=')
	configs[keyvalue[0]]=keyvalue[1]
number_of_node=configs['number_of_node']
ssh_key_file=configs['ssh_key_file']
key_pair=configs['key_pair']
ami_id=configs['ami_id']
vm_type=configs['vm_type']
zk=configs['zk']
zkfolder=zk.replace('.tar.gz','')
jre=configs['jre']
java_home=configs['java_home']
smoketest=configs['smoketest']
stfolder=smoketest.replace('.zip','')
workdir=configs['workdir']
if not int(number_of_node) % 2 or int(number_of_node) < 3:
	printmsg("number of node must be bigger than 3 and odd")
	sys.exit()

cfgfile.close()
#home=os.environ['HOME']

def printmsg(msg):
	timestamp=str(datetime.datetime.now()).split('.')[0]
	print timestamp + " : " + msg



SSH="/usr/bin/ssh -o ConnectTimeout=5 -o StrictHostKeyChecking=no -i " + ssh_key_file + " "
SSH1="/usr/bin/ssh -t -o ConnectTimeout=5 -o StrictHostKeyChecking=no -i " + ssh_key_file + " "
SCP="/usr/bin/scp -i " + ssh_key_file + " " 

#create ec2 conneciton

ec2=boto3.resource('ec2')
if(ec2 == None):
	printmsg("error creating the conneciton, Please check your aws environment settings")
	sys.exit()


#start provision EC instance
printmsg("starting to provision " + number_of_node + " EC instance")
mincount=int(number_of_node)
instances=ec2.create_instances(ImageId=ami_id,MinCount=mincount,MaxCount=mincount,KeyName=key_pair,InstanceType=vm_type)
timeout=10 #in minutes
newInstances=[]
printmsg("waiting " + str(timeout) + " minutes at most for the instance to be ready..")
for instance in instances:
	count=0
	while count<timeout:
		instanceId=instance.instance_id
		instance1=ec2.Instance(instanceId)
		printmsg(instance1.instance_id+ " " + instance1.private_ip_address + " " + instance1.state['Name'])
		if(instance1.state['Name'] !='running'):
			if(count<timeout):
				time.sleep(60)
				count=count+1
				continue
			else:
				printmsg('Error creating instance, the instance not becoming running state after ' + str(timeout) +' seconds')
				sys.exit()
		else:
			newInstances.append(instance1)
			break
			
		

printmsg("sleeping 60 seconds before proceeding")
time.sleep(60)

#test ssh login to the new instances
timeout=10 #in minutes
count=0
for instance in newInstances:
	while count<timeout:
		ip=instance.private_ip_address
		id=instance.instance_id
		printmsg('checking ssh access for servers ' + ip + " " + id)
		#cmd=SSH + ip + ' hostname > /dev/null 2>&1'
		cmd=SSH + ip + " mkdir -p " + zkfolder  + " > /dev/null 2>&1 "
		if os.system(cmd) !=0:
			printmsg("error while trying to test ssh login to servers" + ip + " " + id)
			time.sleep(60)
			count=count+1
			continue
		else:
			break


#copy the source folder to destination servers

zkfile='zoo.cfg'
zkconf='/tmp/' + zkfile
zkcnf=open(zkconf,'w')
zkcnf.write('tickTime=2000\n')
zkcnf.write('dataDir=' + zkfolder +'/dataDir/\n')
zkcnf.write('clientPort=2181\n')
zkcnf.write('initLimit=5\n')
zkcnf.write('syncLimit=2\n')
i=1
for instance in newInstances:
	ip=instance.private_ip_address
	zkcnf.write('server.' + str(i) + '=' + ip + ':2888:3888\n')
	i=i+1

	id=instance.instance_id
	printmsg("copying the binary to the destination server:" + ip+" "+id )
	cmd=SCP + zk + ' ' + ip + ":" +zk + " >/dev/null 2>&1"
	if os.system(cmd) !=0:
		printmsg('error while copying zk file to servers'  + ip + " " + id)
		sys.exit()
	cmd=SCP + jre + ' ' + ip + ":" + jre + " >/dev/null 2>&1"
	if os.system(cmd) !=0:
		printmsg('error while copying jre file to servers'  + ip + " " + id)
		sys.exit()

zkcnf.close()

#Begin installation
i=0
for instance in newInstances:
	i=i+1
	ip=instance.private_ip_address
	id=instance.instance_id
	printmsg("beginning install the package on the destination server:" + ip+" "+id )
	cmd=SSH + ip + " \'cd " + workdir +";/usr/bin/tar -xzvf " + zk + " > /dev/null 2>&1\'"
	if os.system(cmd) !=0:
		printmsg('error while extracting the tar file'  + ip + " " + id + " " + zk)
		sys.exit()
	cmd=SSH + ip + " \'java -version > /dev/null 2>&1\'"
	if os.system(cmd) !=0:
		cmd=SSH1 + ip + " \'sudo  rpm -ivh " + jre + " \' > /dev/null 2>&1"
		if os.system(cmd) !=0:
			printmsg('error while installing the java '  + ip + " " + id + " " + jre)
			sys.exit()

	#copy the zk configuration files
	cmd=SCP + zkconf + ' ' + ip + ":" +zkfolder+ "/conf/ >/dev/null 2>&1"
	if os.system(cmd) !=0:
		printmsg('error while copying zk file to servers'  + ip + " " + id)
		sys.exit()
	
	#create my id file
	cmd=SSH + ip + " \'mkdir " + zkfolder + "/dataDir ; echo " + str(i) + " >"   + zkfolder + "/dataDir/myid\'"
	if os.system(cmd) !=0:
		printmsg('error while creating zk myid file '  + ip + " " + id + " " + zkfolder)
		sys.exit()

	#start service
	printmsg("starting zookeeper service on the destination server:" + ip+" "+id )
	cmd=SSH + ip + " \'export JAVA_HOME=" + java_home + ";" + zkfolder +  "/bin/zkServer.sh start > /dev/null 2>&1\'"
	if os.system(cmd) !=0:
		printmsg('error while starting the zookeeper service '  + ip + " " + id )
		sys.exit()
	
#copy the smoketest file to the last instance for test
printmsg("copying zk-smoketest to the last destination server:" + ip+" "+id )
cmd=SCP + smoketest + ' ' + ip + ":" + smoketest + ">/dev/null 2>&1"
if os.system(cmd) !=0:
	printmsg('error while copying smoketest file to servers'  + ip + " " + id)
	sys.exit()

printmsg("using zk-smoketest to test the zookeeper service on the server:" + ip+" "+id )
cmd=SSH + ip + " \'which unzip> /dev/null 2>&1\'"
if os.system(cmd) !=0:
	printmsg("installing unzip on destination server:" + ip+" "+id)
	cmd=SSH1 + ip + " \'sudo yum -y install unzip.x86_64 \' > /dev/null 2>&1"
	if os.system(cmd) !=0:
		printmsg("error installing unzip")
		sys.exit()
	
cmd1="cd " + workdir +";"
cmd2="unzip " + smoketest + "> /dev/null 2>&1;"
cmd3="cd " + stfolder + ";"
cmd4="PYTHONPATH=lib.linux-x86_64-2.6 LD_LIBRARY_PATH=lib.linux-x86_64-2.6 ./zk-smoketest.py --config "    + zkfolder + "/conf/" + zkfile 
#cmd=SSH + ip + " \'cd " + stfolder + ";PYTHONPATH=lib.linux-x86_64-2.6 LD_LIBRARY_PATH=lib.linux-x86_64-2.6 ./zk-smoketest.py --config "    + zkfolder + "/conf/" + zkfile + "\'"
cmd= SSH + ip + " \'" + cmd1 + cmd2 + cmd3 + cmd4 +"\'"
if os.system(cmd) !=0:
	printmsg('error while using smoketest to test the zookeeper '  + ip + " " + id )
	sys.exit()


