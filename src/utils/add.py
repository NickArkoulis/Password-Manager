from utils.dbconfig import dbconfig
import utils.aesutil
from getpass import getpass
import cryptography

from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives import hashes
# we will use PBKDF2, to derive a strong cryptography key from a password and a random salt
from Crypto.Hash import SHA512
from Crypto.Random import get_random_bytes
import base64

from rich import print as printc
from rich.console import Console

#we encode password, get the salt, save it as salt
def computeMasterKey(masterpass, devsec):
	password = masterpass.encode()
	salt = devsec.encode()
	#key = PBKDF2(password, salt, 32, count=1000000, hmac_hash_module=SHA512)
	kdf = PBKDF2HMAC(
		algorithm=hashes.SHA512(),
		length=32,
		salt=salt,
		iterations=1000000,
	)
	key = kdf.derive(password)
	#output, a 32-byte key
	return key


def addEntry(masterpass, devsec, sitename, siteurl, email, username):
	#get password
	password = getpass("Password: ")

	computeMasterKey(masterpass, devsec)

	maskey = computeMasterKey(masterpass, devsec)

	encrypted = utils.aesutil.encrypt(key=maskey, source=password, keyType="bytes")


	#add the above to database
	db = dbconfig()
	cursor = db.cursor()
	query = "INSERT INTO unizg.entries (sitename, siteurl, email, username, password) values (%s, %s, %s, %s, %s)"
	val = (sitename,siteurl,email,username,encrypted)
	cursor.execute(query, val)
	db.commit()

	printc("[green][+][/green] Added entry ")