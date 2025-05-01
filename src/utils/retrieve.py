from utils.dbconfig import dbconfig
import utils.aesutil #to decrypt the password
import pyperclip

from Crypto.Protocol.KDF import PBKDF2
from Crypto.Hash import SHA512
from Crypto.Random import get_random_bytes
import base64

from rich import print as printc
from rich.console import Console
from rich.table import Table

def computeMasterKey(masterpass,devsec):
	password = masterpass.encode()
	salt = devsec.encode()
	key = PBKDF2(password, salt, 32, count=1000000, hmac_hash_module=SHA512)
	return key

#contains input that the user gives, to retrieve it in the database
def retrieveEntries(masterpass, devsec, search, decryptPassword = False):
	db = dbconfig()
	cursor = db.cursor()

    #form a query, to execute it in database
	query = ""
	#if user does not specify search field
	if len(search)==0:
		query = "SELECT * FROM unizg.entries"
	else:
		#initialize the query
		query = "SELECT * FROM unizg.entries WHERE "
		for i in search:
			#condition
			query+= f"{i} = '{search[i]}' AND "
		query = query[:-5] #to avoid sql syntax error

	cursor.execute(query)
	results = cursor.fetchall()

	if len(results) == 0:
		printc("[yellow][-][/yellow] No results for this search")
		return

    #check if decrypted password is true and length greater than 1, or if user does not want to access the password
	if (decryptPassword and len(results)>1) or (not decryptPassword):
		if decryptPassword:
			printc("[yellow][-][/yellow] More than one result found for the search, therefore not extracting the password. Be more specific.")
		#table, to display the results
		table = Table(title="Results")
		table.add_column("Site Name")
		table.add_column("URL",)
		table.add_column("Email")
		table.add_column("Username")
		table.add_column("Password")

		for i in results:
			#final field, email, username and password will be hidden, we don't want to display it
			#we could have hidden all of them, but we left it this way, so thath you can see it in the table
			table.add_row(i[0], i[1], "{hidden}", "{hidden}", "{hidden}")
		console = Console()
		console.print(table)
		return 

    #if there is exactly 1 result
	if decryptPassword and len(results)==1:
		#compute master key
		maskey = computeMasterKey(masterpass,devsec)

		#decrypt password
		decrypted = utils.aesutil.decrypt(key=maskey,source=results[0][4],keyType="bytes")

		printc("[green][+][/green] Password copied to clipboard")
		#use pyperclip to copy the decrypted password, after decoding it
		pyperclip.copy(decrypted.decode())
    #close the database object
	db.close()