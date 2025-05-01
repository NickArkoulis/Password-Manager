import os 
import sys
import hashlib
import string
import random
from getpass import getpass
from utils.dbconfig import dbconfig

from rich import print as printc
from rich.console import Console

console = Console()

def generateDevicesecret(length=10):
	return ''.join(random.choices(string.ascii_uppercase + string.digits, k = length))


def config():
	# we create the database for the passwords
	db = dbconfig()
	cursor = db.cursor()

	printc("[green][+] Creating new config [/green]")

	try:
		cursor.execute("CREATE DATABASE unizg")
	except Exception as e:
		printc("[red][!] Error, database was not created.")
		console.print_exception(show_locals=True)
		sys.exit(0)
	# with except, we handle exception in a better way
	printc("[green][+][/green] Database 'unizg' created")

	# 1st table, store the hash of master password, first hash it, then store it, for security
	query = "CREATE TABLE unizg.secrets (masterkey_hash TEXT NOT NULL, device_secret TEXT NOT NULL)"
	res = cursor.execute(query)
	printc("[green][+][/green] Table 'secrets' created.")

	#2nd table, for new entries user enters in password manager
	query = "CREATE TABLE unizg.entries (sitename TEXT NOT NULL, siteurl TEXT NOT NULL, email TEXT, username TEXT, password TEXT NOT NULL)" 
	# password here is encrypted, not plain text
	res = cursor.execute(query)
	printc("[green][+][/green] Table 'entries' created.")


	#input the master password and compute the hash of it
	while 1:
		masterpass = getpass("Choose a Master Password: ")
		if masterpass==getpass("Re-type: ") and masterpass!="":
			break
		printc("[yellow][-] Try again! [/yellow]")

	#hash master password
	hashed_masterpass = hashlib.sha256(masterpass.encode()).hexdigest()
	printc("[green][+][/green] The Hash of Master Password was generated!")

	#generate device secret
	devsec = generateDevicesecret()
	printc("[green][+][/green] Device Secret was generated!")

	#add the above in the database
	query = "INSERT INTO unizg.secrets (masterkey_hash, device_secret) values (%s, %s)"
	val = (hashed_masterpass, devsec)
	cursor.execute(query, val)
	db.commit()

	printc("[green][+][/green] Added to the database!")
	printc("[green][+][/green] Configuration done!")

	db.close()

#call config function
config()