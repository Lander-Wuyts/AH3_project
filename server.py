##########################
### INSTALLING MODULES ###
##########################

import subprocess
import sys

def install(package):
    subprocess.check_call([sys.executable, "-m", "pip", "install", package])

# Installation of modules
# install('flask')
# install('openpyxl')
# install('mysql-connector-python')
# install('squalchemy')
# install('pdfkit')

###############
### IMPORTS ###
###############

# Current directory
import os

# Producten toevoegen, verwijderen
import openpyxl             # pip install openpyxl
from pathlib import Path
import mysql.connector      # pip install mysql-connector-python

# Rapport opstellen
from sqlalchemy import create_engine        # pip install sqlalchemy
import pandas as pd   
import pdfkit                               # pip install pdfkit
from datetime import datetime 

# Email versturen
import smtplib
from datetime import datetime
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email import encoders

# Python scripts
import Producten_toevoegen, Producten_verwijderen, Rapport_opstellen, Email_direct

# Flask
from flask import Flask, render_template, redirect

#################
### VARIABLES ###
#################

# Excel-documents
path_add_products = os.getcwd()
name_add_products = 'Producten toevoegen.xlsx'
path_remove_products = os.getcwd()
name_remove_products = 'Producten verwijderen.xlsx'

# MySQL
mysql_host="127.0.0.1"  # "localhost" or "127.0.0.1"
mysql_user="unicenta"  # "root" or "unicenta"
mysql_password="abc123!"  # "1234" or "abc123!"
mysql_database="unicentaopos"

# Pdfkit MySQL
username = 'root'
password = '1234'
host = '127.0.0.1'  # "localhost" or "127.0.0.1"
database = 'unicentaopos'

path_wkhtmltopdf = os.getcwd() + '\\wkhtmltopdf\\bin\\wkhtmltopdf.exe'
print(path_wkhtmltopdf)

# E-mail
message = """
Geachte,

In de bijlage kan u het document vinden met de overschot van deze week.

Met vriendelijke groeten
"""

sender = 'supermarkt.test@gmail.com'
password = '2ccs02AH3'
receiver = 'vzwsupermarkt.test@gmail.com'

reports_folder = 'Reports'

######################
### INITIALIZATION ###
######################

# MySQL
mydb = mysql.connector.connect(
    host=mysql_host,
    user=mysql_user,
    password=mysql_password,
    database=mysql_database
)

db_cursor = mydb.cursor()

# Pdfkit MySQL
db_connection_str = 'mysql+pymysql://{}:{}@{}/{}'.format(username, password, host, database)
db_connection = create_engine(db_connection_str)
config = pdfkit.configuration(wkhtmltopdf=path_wkhtmltopdf)

# E-mail
msg = MIMEMultipart()

# Flask
app = Flask(__name__)

#########################
### EXECUTION OF CODE ###
#########################

# Homepage
@app.route('/')
def index():
  return render_template('index.html')

# "Scan producten in"-knop
@app.route('/add-product/')
def add_product():
  print ('Adding products to expired database')

  scanned_products = Producten_toevoegen.read_excel(path_add_products, name_add_products)
  for scanned_product in scanned_products:
      barcode_db_id = Producten_toevoegen.find_id_db(db_cursor, scanned_product[0])
      Producten_toevoegen.write_entry_expiration_db(mydb, db_cursor, barcode_db_id, scanned_product)
  
  return redirect("http://127.0.0.1:5000/")

# "Scan producten uit"-knop
@app.route('/remove-product/')
def remove_product():
  print('Removing products from expired database')

  sold_products = Producten_verwijderen.read_excel(path_remove_products, name_remove_products)
  Producten_verwijderen.loop_remove_products(mydb, db_cursor, sold_products)

  return redirect("http://127.0.0.1:5000/")

# "PDF-verslag"-knop
@app.route('/create-report/')
def create_report():
  print('Creating a pdf report in the Reports folder')
  current_date = datetime.now()

  db_info = Rapport_opstellen.pandas_read_db()
  Rapport_opstellen.build_pdf_html(config, db_info)

  return redirect("http://127.0.0.1:5000/")

# "Verstuur verslag via mail"-knop
@app.route('/send-email/')
def send_email():
  print("Sending email")

  Email_direct.send_mail(msg, sender, receiver, message, reports_folder)

  return redirect("http://127.0.0.1:5000/")

# "Open HTML verslag"-knop
@app.route('/open-report/')
def open_redirect():
  print("Toon rapport")

  return render_template('Report.html')

# Debug mode?
if __name__ == '__main__':
  app.run(debug=True)
