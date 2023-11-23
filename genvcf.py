import csv
import logging
import argparse
import os
import psycopg2 as pg
import requests
import sys

logger = None

class HRException(Exception): pass  


#def details_from_csv(csvfile):
#  data = []
#  with open(csvfile,'r') as f:
#    reader = csv.reader(f)
#    for item in reader:
#      data.append(item)
#  return data
  

def parse_args():
    parser = argparse.ArgumentParser(description="HR management tools")
    parser.add_argument("-d","--dbname", help="Create database table", action='store', default='employee')
    parser.add_argument("-v", "--verbose", help="Print detailed logging", action='store_true', default=False)
    #parser.add_argument("-n", "--number", help="Number of records to generate", action='store', type=int, default=100)
    subparser = parser.add_subparsers(dest='subcommand',help = 'sub-command help')
  
    
    #inittb subcommand # Done adding the changes
    parser_initdb = subparser.add_parser("inittb",help="Initialization of table in the database")
    
   
    #load subcommand
    parser_load = subparser.add_parser("load" ,help="Load data to database from csvfile")
    parser_load.add_argument("-c","--csv",help="Providing name of csv file",type=str)
    
    #retreiving data from database and generate vcard for a particular employee
    parser_retrieve = subparser.add_parser("rtr" ,help="retrieve data from database")
    parser_retrieve.add_argument("--vcard", help="Generate vcard details of employee_id to show it on terminal",action="store_true",default = False)
    parser_retrieve.add_argument("-i", "--id", help="ID of the employee whose data needs to be generated",type=str)
    parser_retrieve.add_argument("--vcf",help="Geenrate vcard file",action="store_true",default=False)
    parser_retrieve.add_argument("--qrcd",help="Generate qrcode file",action="store_true",default=False)
    
    #generate vcard files for a specified number of employee
    parser_generate = subparser.add_parser("genvcard",help="Generate vcards for the data")
    parser_generate.add_argument("-n", "--number", help="Number of records to generate", action='store', type=int,default=10)
    parser_generate.add_argument("--qrcd",help="Generate qrcode file",action="store_true",default=False)
    
    #enter data into leaves table
    parser_initlv = subparser.add_parser("initlv",help="Input data into leaves table")
    parser_initlv.add_argument("date", help="date of the employee's leave")
    parser_initlv.add_argument("employee_id",help="Employee id from details table")
    parser_initlv.add_argument("reason",help="Reason for leave")
    
    #Insert data into designation table
    parser_initds = subparser.add_parser("initds",help="Input data into leaves table")
    parser_initds.add_argument("designation", help="designation of employees")
    parser_initds.add_argument("numoflv",help="number of leaves alloted to each designation")
    
    #retrieve leave data from leaves table and designation table
    parser_initrtrlv = subparser.add_parser("rtrlv",help="Input data into leaves table")
    parser_initrtrlv.add_argument("employee_id", help="employee id of whome the leave data needs to be retrieved")
    
    #Generate details of employees leaves on csv file
    parser_initcsv = subparser.add_parser("rtrcsv",help="Generate details of employees leaves on csv file")
    
    #parser_load.add_argument("-n", "--number", help="Number of records to generate", action='store', type=int, default=100)
    #parser_load.add_argument("-s", "--sizeqr", help="Size of qr code png", action='store', type=int, default=500)
    #parser_load.add_argument("-q", "--qrcode", help="Generate both qrcode and vcard files", action='store_true', default= False )
    #parser_load.add_argument("-a", "--address", help="Provide an address other than default address", action='store', default= '100 Flat Grape Dr.;Fresno;CA;95555;United States of America' )
    
    
    #retrieve count from new table 
    parser_ct = subparser.add_parser("rtrnt",help="Retrieve count of absents")
    parser_ct.add_argument("-u","--user", help="Adding user name of database",action="store",type=str,default='althaf')
    parser_ct.add_argument("-d","--dbname", help="Adding database name",action="store",type=str,default='employee')
    parser_ct.add_argument("-i","--userid", help="id of the user whose leave data needs to be obtained",action="store",type=int,default=1)
    
    #adding data to leaves table
    parser_file = subparser.add_parser("adddata",help="Adding data to leaves table")
    parser_file.add_argument("-u","--user", help="Adding user name of database",action="store",type=str,default='althaf')
    parser_file.add_argument("-d","--dbname", help="Adding database name",action="store",type=str,default='employee')
    parser_file.add_argument("-f","--filename", help="id of the user whose leave data needs to be obtained",action="store",type=str,default='leaves.sql')  
    
    #adding data to leaves table witthout sql file
    parser_sq = subparser.add_parser("sql",help="Adding data to leaves table")
    parser_sq.add_argument("-u","--user", help="Adding user name of database",action="store",type=str,default='althaf')
    parser_sq.add_argument("-d","--dbname", help="Adding database name",action="store",type=str,default='employee')
    parser_sq.add_argument("-t","--date", help="Input data to add it to second table", action="store",type=str,default='0000-00-00')
    parser_sq.add_argument("-i","--id", help="Input data of user id", action="store",type=int,default=0)     
    parser_sq.add_argument("-r","--reason", help="Input data regarding cause", action="store",type=str,default='NONE')
    
    
    
    args = parser.parse_args() 
    return args


def logger(is_logger):
    global logger
    if is_logger:
      level = logging.DEBUG
    else:
      level = logging.INFO
    logger = logging.getLogger("genvcf_log")
    handler = logging.StreamHandler()
    handler.setLevel(level)
    handler.setFormatter(logging.Formatter("[%(levelname)s] %(asctime)s | %(filename)s:%(lineno)d | %(message)s"))
    logger.setLevel(logging.DEBUG)
    logger.addHandler(handler)


#def data_from_details(details,number):
#  data = []
#  for i in range(0,number):
#     data.append(details[i])
#  return data


# Database implementation starts

#def create_database(user,dbase):
#  conn = pg.connect(database="postgres",user=user)
#  cursor = conn.cursor()
#  conn.autocommit = True
#  create_database =  f"CREATE DATABASE {dbase}"
#  cursor.execute(create_database)
#  print("Creation of database is successful")
#  conn.close()





## Clarified error and built new function to create table
def create_table(args):
  with open("init.sql",'r') as f:
    query = f.read()
    logger.debug(query)
  try:
    conn = pg.connect(dbname=args.dbname)  
    cursor = conn.cursor()
    cursor.execute(query)
    conn.commit()
    conn.close()
  except pg.OperationalError as e:
    raise HRException(f'database "{args.dbname}" not found')



#Details table alteration starts

def truncate_table(user,dbname):
  conn = pg.connect(f"dbname={dbname} user={user}")
  cursor = conn.cursor()
  truncate_table = "TRUNCATE TABLE details RESTART IDENTITY CASCADE"
  cursor.execute(truncate_table)
  conn.commit()
  conn.close()
  
  
## Done editing this part as per the request
def add_data_to_table_details(args):
  conn = pg.connect(dbname=args.dbname)
  cursor = conn.cursor()
  with open(args.csv,'r') as f:
    reader = csv.reader(f)
    for last_name,first_name,title,email,ph_no in reader:
      logger.debug("Inserted data of %s",email)
      insert_info = "INSERT INTO details (lastname,firstname,title,email,phone_number) VALUES (%s,%s,%s,%s,%s)"
      cursor.execute(insert_info,(last_name,first_name,title,email,ph_no))
    conn.commit()
  print("data inserted")
  conn.close()
 
 
 
# fetchone we get details in a tupule fetchall we get details in a tupule which is present inside a list      
## Designed based on the request 
def retriving_data_from_database(args):
  conn = pg.connect(dbname=args.dbname)
  cursor = conn.cursor()
  query = "SELECT lastname,firstname,title,email,phone_number FROM details where serial_number = %s"
  cursor.execute(query,(args.id,))
  conn.commit()
  lastname,firstname,title,email,phone_number = cursor.fetchone()
  print(f"""Name        : {firstname} {lastname}
Designation : {title}
Email       : {email}
Phone       : {phone_number}""")
  if args.vcard:
     print("\n",implement_vcf(lastname,firstname,title,email,phone_number))
  if args.vcf:
    if not os.path.exists('worker_vcf'):
      os.mkdir('worker_vcf') 
    imp_vcard = implement_vcf(lastname,firstname,title,email,phone_number)
    with open(f'worker_vcf/{email}.vcf','w') as j:
       j.write(imp_vcard)
  if args.qrcd:
     if not os.path.exists('worker_vcf'):
       os.mkdir('worker_vcf')
     imp_qrcode = implement_qrcode(lastname,firstname,title,email,phone_number)
     with open(f'worker_vcf/{email}.qr.png','wb') as f:
        f.write(imp_qrcode)
     logger.info(f"Done generating qrcode of {email}")
  conn.close()


def genrate_vcard_file(args):
  if not os.path.exists('worker_vcf'):
    os.mkdir('worker_vcf')
  count = 1
  conn = pg.connect(dbname=args.dbname)
  cursor = conn.cursor()
  query = "SELECT lastname,firstname,title,email,phone_number FROM details"
  cursor.execute(query)
  data = cursor.fetchall()
  details = []
  for i in range(0,args.number):
    details.append(data[i])
    for lastname,firstname,title,email,phone_number in details:
        imp_vcard = implement_vcf(lastname,firstname,title,email,phone_number)
        logger.debug("Writing row %d", count)
        count +=1
        with open(f'worker_vcf/{email}.vcf','w') as j:
           j.write(imp_vcard)
        if args.qrcd:
           imp_qrcode = implement_qrcode(lastname,firstname,title,email,phone_number)
           with open(f'worker_vcf/{email}.qr.png','wb') as f:
             f.write(imp_qrcode)
    logger.info(f"Done generating qrcode of {email}")
  logger.info("Done generating vCards") 
  conn.close() 


#Insert data into table leaves
def add_data_to_leaves_table(args):
  conn = pg.connect(dbname=args.dbname)
  cursor = conn.cursor()
  insert_info = """INSERT INTO leaves (date,employee_id,reason) VALUES (%s,%s,%s)"""
  cursor.execute(insert_info,(args.date,args.employee_id,args.reason))
  conn.commit()
  print("data inserted")
  conn.close()


#Insert data into designation table
def add_data_to_designation_table(args):
  conn = pg.connect(dbname=args.dbname)
  cursor = conn.cursor()
  insert_info = "INSERT INTO designation (designation,num_of_leaves) VALUES (%s,%s)"
  cursor.execute(insert_info,(args.designation,args.numoflv))
  conn.commit()
  print("data inserted")
  conn.close()


#retrieve number of leaves remaining for an employee
def retrive_data_from_new_table(args):
  conn = pg.connect(dbname = args.dbname)
  cursor = conn.cursor()
  rtr_count = f"""select count (d.serial_number) as count, d.firstname, d.lastname , d.email, g.designation , g.num_of_leaves 
                  from details d join leaves l on d.serial_number = l.employee_id 
                  join designation g on d.title = g.designation 
                  where d.serial_number={args.employee_id} group by d.serial_number,d.firstname,d.email,g.num_of_leaves,g.designation;"""
  cursor.execute(rtr_count,(args.employee_id,))
  #print("Execution successfull")
  data = cursor.fetchall()
  if data != []: 
     for i in data:
       leaves = i[0]
       max_leaves = i[5]
       available_leaves = max_leaves - leaves
       d = f"""Name of employee : {i[1]} {i[2]}
Email : {i[3]}
Designation : {i[4]}
Maximum alloted leaves : {i[5]}
Available leaves = {available_leaves}"""
       conn.commit()
  if data == []:
     cursor.execute(f"""select d.num_of_leaves as number,t.firstname,t.lastname , t.email, d.designation from designation d 
                      join details t on d.designation=t.title where t.serial_number = {args.employee_id};""")
     leaves = cursor.fetchall()
     for i in leaves:
       d = f"""Name of employee : {i[1]} {i[2]}
Email : {i[3]}
Designation : {i[4]}
Maximum alloted leaves : {i[0]}
Available leaves = {i[0]}"""
     
     conn.commit()
  conn.close()


#Generate details of employees leaves on csv file
def generate_leave_csv(args):
  conn = pg.connect(dbname=args.dbname)
  cursor = conn.cursor()
  insert_info = ""
  cursor.execute(insert_info,(args.designation,args.numoflv))
  conn.commit()
  print("data inserted")
  conn.close()
  

#Implementation of details table ends

#def truncate_table_leaves(user,dbname,filename):
#  with open(f"{filename}",'w+') as f:
#     f.close()
#  conn = pg.connect(f"dbname={dbname} user={user}")
#  cursor = conn.cursor()
#  truncate_table = "TRUNCATE TABLE leaves RESTART IDENTITY CASCADE"
#  cursor.execute(truncate_table)
#  conn.commit()
#  conn.close()

  
#def create_new_table(user,dbname):
#  #truncate_table_leaves(user,dbname)
#  conn = pg.connect(f"dbname={dbname} user={user}")
#  cursor = conn.cursor()
#  create_table = """CREATE TABLE leaves (serial_number SERIAL PRIMARY KEY,
#                                         date DATE,
#                                         employee_id INTEGER REFERENCES details(serial_number),
#                                       reason VARCHAR(50),UNIQUE (date,employee_id))"""
#  cursor.execute(create_table)
#  print("New table created successfully")
#  conn.commit()
#  conn.close()
  
#def add_new_data_to_new_table(user,dbname,filename):
#  conn = pg.connect(f"dbname={dbname} user={user}")
#  cursor = conn.cursor()
#  with open(f"{filename}",'r') as f:
#    cursor.execute(f.read())
#    conn.commit()
# conn.close()
# f.close()
  
  
#def add_data_to_new_table(user,dbname,date,employee_id,reason):
#  conn = pg.connect(f"dbname={dbname} user={user}")
#  cursor = conn.cursor()
#  insert_info = """INSERT INTO leaves (date,empoyee_id,reason) VALUES (%s,%d,%s)"""
#  cursor.execute(insert_info,(date,employee_id,reason))
#  conn.commit()
#  print("data inserted")
#  conn.close()
  
  

  
  
  
  
  
  
  
# Database implementation ends

def implement_vcf(last_name,first_name,job,email,ph_no):
  return f"""
BEGIN:VCARD
VERSION:2.1
N:{last_name};{first_name}
FN:{first_name} {last_name}
ORG:Authors, Inc.
TITLE:{job}
TEL;WORK;VOICE:{ph_no}
ADR;WORK:;;100 Flat Grape Dr.;Fresno;CA;95555;United States of America
EMAIL;PREF;INTERNET:{email}
REV:20150922T195243Z
END:VCARD
"""
  


#def generate_vcf(details,address):
#  if not os.path.exists('worker_vcf'):
#    os.mkdir('worker_vcf')
#  count = 1
#  for first_name,last_name,job,email,ph_no in details:
#       imp_vcard = implement_vcf(first_name,last_name,job,email,ph_no,address)
#       logger.debug("Writing row %d", count)
#       count +=1
#       with open(f'worker_vcf/{email}.vcf','w') as j:
#          j.write(imp_vcard)
#  logger.info("Done generating vCards")  
     
       
  
def implement_qrcode(first_name,last_name,job,email,ph_no):
   reqs = requests.get(f"""https://chart.googleapis.com/chart?cht=qr&chs=500x500&chl=BEGIN:VCARD
VERSION:2.1
N:{last_name};{first_name}
FN:{first_name} {last_name}
ORG:Authors, Inc.
TITLE:{job}
TEL;WORK;VOICE:{ph_no}
ADR;WORK:;;100 Flat Grape Dr.;Fresno;CA;95555;United States of America
EMAIL;PREF;INTERNET:{email}
REV:20150922T195243Z
END:VCARD""")
   return reqs.content
       

       
#def generate_qrcode(details,size,address):
#  if not os.path.exists('worker_vcf'):
#    os.mkdir('worker_vcf')
#  count = 1
#  for first_name,last_name,job,email,ph_no in details:
#    imp_qrcode = implement_qrcode(first_name,last_name,job,email,ph_no,size,address)
#    logger.debug("Writing row %d", count)
#    count +=1
#    with open(f'worker_vcf/{email}.qr.png','wb') as f:
#      f.write(imp_qrcode)
#  logger.info("Done generating qr code files")
  
  
def main():
  try:
    args = parse_args()
    logger(args.verbose)
    operations = { "inittb"   : create_table,
                   "load"     : add_data_to_table_details,
                   "rtr"      : retriving_data_from_database,
                   "genvcard" : genrate_vcard_file,
                   "initlv"   : add_data_to_leaves_table,
                   "initds"   : add_data_to_designation_table,
                   "rtrlv"    : retrive_data_from_new_table,
                   "rtrcsv"   : generate_leave_csv
                 }
    operations[args.subcommand](args)
    #if args.subcommand == "inittb":
      #create_table(args)
    #if args.subcommand == "load":
      #add_data_to_table_details(args)
    #if args.subcommand == "rtr":
      # retriving_data_from_database(args)
       #if args.qrcode:
        #  generate_qrcode(details,args.sizeqr,args.address)
    if args.subcommand == "createtb":
       create_new_table(args.user,args.dbname)
    if args.subcommand == "rtrct":
       retrive_data_from_new_table(args.user,args.dbname,args.userid)
    if args.subcommand == "adddata":
       add_new_data_to_new_table(args.user,args.dbname,args.filename)
    if args.subcommand == "trct":
       truncate_table_leaves(args.user,args.dbname,args.filename)
    if args.subcommand == "sql":
       add_data_to_new_table(args.user,args.dbname,args.date,args.id,args.reason)
  except HRException as e:
     logger.error("Program aborted due to %s", e)
     sys.exit(-1)
     
if __name__ == '__main__':
   main()    
   
   
