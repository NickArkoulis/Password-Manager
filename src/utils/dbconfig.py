import mysql.connector #import the database

#import rich library, for better visualization
from rich import print as printc
from rich.console import Console

console = Console()

def dbconfig():
	try:
		db = mysql.connector.connect(
			host='localhost' , 
			user='unizg' ,
			passwd='123456'
		)

	except Exception as e:
		console.print_exception(show_locals=True)

	#return database object
	return db