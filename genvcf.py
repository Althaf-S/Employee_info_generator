import csv
import logging
import argparse
import os
import psycopg2 as pg
import requests
import sys

logger = None

class HRException(Exception): pass  


def parse_args():
    parser = argparse.ArgumentParser(description="HR management tools")
    parser.add_argument("-d","--dbname", help="Create database table", action='store', default='employee')
    parser.add_argument("-v", "--verbose", help="Print detailed logging", action='store_true', default=False)
    #parser.add_argument("-n", "--number", help="Number of records to generate", action='store', type=int, default=100)
    subparser = parser.add_subparsers(dest='subcommand',help = 'sub-command help')
  
    #inittb subcommand 
    parser_initdb = subparser.add_parser("inittb",help="Initialization of table in the database")
    
   
    #load subcommand
    parser_load = subparser.add_parser("load" ,help="Load data to database from csvfile")
    parser_load.add_argument("file",help="Providing name of csv file",type=str)
    
    #retreiving data from database and generate vcard for a particular employee
    parser_retrieve = subparser.add_parser("rtr" ,help="retrieve data from database")
    parser_retrieve.add_argument("id", help="ID of the employee whose data needs to be generated",type=str)
    parser_retrieve.add_argument("--vcard", help="Generate vcard details of employee_id to show it on terminal",action="store_true",default = False)
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
    #parser_initds.add_argument("designation", help="designation of employees")
    #parser_initds.add_argument("numoflv",help="number of leaves alloted to each designation")
    
    #retrieve leave data from leaves table and designation table
    parser_initrtrlv = subparser.add_parser("rtrlv",help="Input data into leaves table")
    parser_initrtrlv.add_argument("employee_id", help="employee id of whome the leave data needs to be retrieved")
    
    #Generate details of employees leaves on csv file
    parser_initcsv = subparser.add_parser("rtrcsv",help="Generate details of employees leaves on csv file")
    parser_initcsv.add_argument("-f","--filename",help="Provide file name for generating csv, only file name and no file extention is needed",action='store',default="lv")
       
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



# Database implementation starts


## Create details,leaves,designation table
def create_table(args):
  with open("init.sql",'r') as f:
    query = f.read()
    logger.debug(query)
  try:
    conn = pg.connect(dbname=args.dbname)  
    cursor = conn.cursor()
    cursor.execute(query)
    conn.commit()
    logger.info("Done creating tables")
    conn.close()
  except pg.OperationalError as e:
    raise HRException(f'database "{args.dbname}" not found')



#Details table alteration starts

def truncate_table(user,dbname):
  conn = pg.connect(dbname=args.dbname)
  cursor = conn.cursor()
  truncate_table = "TRUNCATE TABLE details RESTART IDENTITY CASCADE"
  cursor.execute(truncate_table)
  conn.commit()
  conn.close()
  
  
#Insert data into details table from csv 
def add_data_to_table_details(args):
  conn = pg.connect(dbname=args.dbname)
  cursor = conn.cursor()
  with open(args.file,'r') as f:
    reader = csv.reader(f)
    for last_name,first_name,title,email,ph_no in reader:
      logger.debug("Inserted data of %s",email)
      insert_info = "INSERT INTO details (lastname,firstname,title,email,phone_number) VALUES (%s,%s,%s,%s,%s)"
      cursor.execute(insert_info,(last_name,first_name,title,email,ph_no))
    conn.commit()
  logger.info("data inserted")
  conn.close()
 
 
 
# fetchone we get details in a tupule fetchall we get details in a tupule which is present inside a list      
#Genereate vcard,qrcode for a single employee and also show vcard info on terminal
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
    logger.info(f"Done generating vcard of {email}")
  if args.qrcd:
     if not os.path.exists('worker_vcf'):
       os.mkdir('worker_vcf')
     imp_qrcode = implement_qrcode(lastname,firstname,title,email,phone_number)
     with open(f'worker_vcf/{email}.qr.png','wb') as f:
        f.write(imp_qrcode)
     logger.info(f"Done generating qrcode of {email}")
  conn.close()


#Generate vcard and qrcode for given number of employees
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
  logger.info("data inserted")
  conn.close()


#Insert data into designation table
def add_data_to_designation_table(args):
  with open("designation.sql",'r') as f:
    query = f.read()
  conn = pg.connect(dbname=args.dbname)  
  cursor = conn.cursor()
  cursor.execute(query)
  conn.commit()
  f.close()
  logger.info("Data inserted into designation table")
  conn.close()


#retrieve number of leaves remaining for an employee (single employee)
def retrive_data_from_new_table(args):
  conn = pg.connect(dbname = args.dbname)
  cursor = conn.cursor()
  rtr_count = f"""select count (d.serial_number) as count, d.firstname, d.lastname , d.email, g.designation , g.num_of_leaves 
                  from details d join leaves l on d.serial_number = l.employee_id 
                  join designation g on d.title = g.designation 
                  where d.serial_number= %s group by d.serial_number,d.firstname,d.email,g.num_of_leaves,g.designation;"""
  cursor.execute(rtr_count, (args.employee_id,))
  data = cursor.fetchall()
  if data != []: 
     for count_serial_number,firstname,lastname,email,designation,num_of_leaves in data:
       leaves = count_serial_number
       max_leaves = num_of_leaves
       leaves = max_leaves - leaves
       if leaves <= 0:
         available_leaves = 0
       else:
         available_leaves = leaves
       d = f"""Name of employee : {firstname} {lastname}
Email : {email}
Designation : {designation}
Maximum alloted leaves : {num_of_leaves}
Available leaves : {available_leaves}
Total leaves taken : {count_serial_number}"""
       print(d)
       conn.commit()
  if data == []:
     cursor.execute("""select d.num_of_leaves as number,t.firstname,t.lastname , t.email, d.designation from designation d 
                      join details t on d.designation=t.title where t.serial_number = %s;""", (args.employee_id,))
     leaves = cursor.fetchall()
     for num_of_leaves,firstname,lastname,email,designation in leaves:
       d = f"""Name of employee : {firstname} {lastname}
Email : {email}
Designation : {designation}
Maximum alloted leaves : {num_of_leaves}
Available leaves : {num_of_leaves}
Total leaves taken : 0"""
     print(d) 
     conn.commit()
  conn.close()


#Generate details of employees leaves on csv file
def generate_leave_csv(args):
  with open(f"{args.filename}.csv","w") as f:
    data = csv.writer(f)
    a = "Employee_id","firstname","lastname","email","title","Total number of leaves","Leaves left"
    data.writerow(a)
  f.close()
  conn = pg.connect(dbname=args.dbname)
  cursor = conn.cursor()
  cursor.execute("select count(serial_number) from details")
  x = cursor.fetchall()
  for i in x:
    count = i[0]
  for i in range (1,count+1):
    insert_info = """select l.employee_id from leaves l join details d on l.employee_id = d.serial_number where d.serial_number= %s"""
    cursor.execute(insert_info, (i,))
    data = (cursor.fetchall())
    if data == []:
      info = f"select d.serial_number,d.firstname,d.lastname,d.email,d.title,g.num_of_leaves from details d join designation g on g.designation = d.title where d.serial_number = %s"
      cursor.execute(info, (i,))
      n = cursor.fetchall()
      for serial_number,firstname,lastname,email,title,num_of_leaves in n:
        with open(f"{args.filename}.csv","a") as f:
          data = csv.writer(f)
          a = serial_number,firstname,lastname,email,title,num_of_leaves,num_of_leaves
          data.writerow(a)
        f.close()
        #print(l[0],l[1],l[2],l[3],l[4],"Total no. of leaves :-",l[5],"Leaves left :-",l[5])
    else:
      info = "select d.serial_number,d.firstname,d.lastname,d.email,d.title,g.num_of_leaves from details d join designation g on g.designation = d.title where d.serial_number = %s"
      cursor.execute(info, (i,))
      n = cursor.fetchall()
      for serial_number,firstname,lastname,email,title,num_of_leaves in n:
        num_leaves = num_of_leaves
      leaves = "select count(l.employee_id),l.employee_id from leaves l where l.employee_id = %s group by l.employee_id"
      cursor.execute(leaves, (i,))
      m = cursor.fetchall()
      for count_employee_id,employee_id in m:
        count = count_employee_id
      leaves = num_leaves - count
      if leaves <= 0:
        leaves_left = 0
      else:
        leaves_left = leaves
      with open(f"{args.filename}.csv","a") as f:
          data = csv.writer(f)
          a = serial_number,firstname,lastname,email,title,num_of_leaves,leaves_left
          data.writerow(a)
      f.close()
      #kprint(j[0],j[1],j[2],j[3],j[4],"Total no. of leaves :-",j[5],"Leaves left :-",leaves_left)
    conn.commit()
  logger.info("CSV file consisting of employee's leave data is generated")
  conn.close()  
  
  
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

  except HRException as e:
     logger.error("Program aborted due to %s", e)
     sys.exit(-1)
     
if __name__ == '__main__':
   main()    
   
   
