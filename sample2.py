import boto3
import time
import datetime
import os
from datetime import datetime, timezone
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication
from email.mime.multipart import MIMEMultipart
import csv

def user_list(client):
	userlist = []
	client = boto3.client("iam")
	listusers = client.list_users()
	for users in listusers['Users']:
		userlist.append(users['UserName'])
	return userlist

def check_age(client,user):
	access_keys = client.list_access_keys(UserName=user)
	for Acs_ID in access_keys['AccessKeyMetadata']:
		start_date = Acs_ID['CreateDate']
		# return start_date
		current_date = datetime.now(timezone.utc)
		key_age = ((current_date - start_date).days)
		return key_age,Acs_ID['AccessKeyId']


def key_rotation(client,access_key,user):
	making_inactive = client.update_access_key(AccessKeyId=access_key,Status='Active',UserName=user)
	delete = client.delete_access_key(UserName=user,AccessKeyId=access_key)
	create = client.create_access_key(UserName=user)
	return create

def convert_csv(create):
	lst = []
	user_name = create['AccessKey']['UserName']
	Access_Key = create['AccessKey']['AccessKeyId']
	Secret_Key = create['AccessKey']['SecretAccessKey']
	dicts = dict()
	dicts["ListofUsers"] = user_name
	dicts["AccessKeys"] = Access_Key
	dicts["SecretKey"] = Secret_Key
	lst.append(dicts)
	file_name = "test1.csv"
	fields = ['ListofUsers', 'AccessKeys', 'SecretKey']
	with open(file_name, 'w') as writeFile:  
		writer = csv.DictWriter(writeFile, fieldnames = fields) 
		writer.writeheader() 
		writer.writerows(lst)
	writeFile.close()
	
	return file_name

def ses_email(client2,file_name):
	file = MIMEMultipart('mixed')
	msg = MIMEApplication(open(file_name, 'r').read())
	msg.add_header('Content-Disposition', 'attachment', filename=os.path.basename(file_name))
	file.attach(msg)
	send_mail = client2.send_raw_email(Source="joshva0894@gmail.com",Destinations = ['joshva0894@gmail.com'],RawMessage ={"Data": file.as_string(),})
	print ("E-mail sent Successfully !@!@!@!@!@!@!")
	
def lambda_handler():
	client = boto3.client('iam')
	client2 = boto3.client('ses')
	users = user_list(client)
	# print (users)
	for user in users:
		age,access_key = check_age(client,user)
		print (age,access_key)
		# if age >= 0:
		# 	rotate = key_rotation(client,access_key,user)
		# 	rotation = convert_csv(rotate)
		# 	ses_email(client2,rotation)

lambda_handler()