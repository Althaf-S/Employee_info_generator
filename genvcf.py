import argparse
import csv
import configparser
import logging
import os
import sys

import psycopg2 as pg
import requests
import sqlalchemy as sa

import models
import web

logger = None

class HRException(Exception): pass  

def database_name(dbname):
  config = configparser.ConfigParser()
  config.read('config.ini')
  config.set('Database','dbname',dbname)
  with open('config.ini','w') as config_file:
     config.write(config_file)

def parse_args():
    
    config = configparser.ConfigParser()
    config.read('config.ini')
    
    parser = argparse.ArgumentParser(description="Employee management tools")
    parser.add_argument("-d","--dbname", help="Create database table", action='store',type=str,default=config.get('Database','dbname'))
    parser.add_argument("-v", "--verbose", help="Print detailed logging", action='store_true', default=False)
    subparser = parser.add_subparsers(dest='subcommand',help = 'sub-command help')
  
    web_parser = subparser.add_parser("web", help="To run program on web")
    
    #inittb subcommand 
    parser_initdb = subparser.add_parser("initdb",help="Initialization of table in the database")
    
   
    #load subcommand
    parser_load = subparser.add_parser("import" ,help="Load data to database from csvfile")
    parser_load.add_argument("file",help="Providing name of csv file",type=str)
    
    #retreiving data from database and generate vcard for a particular employee
    parser_retrieve = subparser.add_parser("empinfo" ,help="retrieve data from database")
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
    parser_initlv.add_argument("date", help="date of the employee's leave (Date format is : YYYY-MM-DD)")
    parser_initlv.add_argument("employee_id",help="Employee id from details table")
    parser_initlv.add_argument("reason",help="Reason for leave")

    
    #retrieve leave data from leaves table and designation table
    parser_initrtrlv = subparser.add_parser("emplv",help="Obtain data regarding leaves of employee")
    parser_initrtrlv.add_argument("employee_id", help="employee id of whome the leave data needs to be retrieved")
    
    #Generate details of employees leaves on csv file
    parser_initcsv = subparser.add_parser("leavecsv",help="Generate details of employees leaves on csv file")
    parser_initcsv.add_argument("-f","--filename",help="Provide file name for generating csv, only file name and no file extention is needed",action='store',default="lv")
    
    #Update tables:
    parser_uptbemp = subparser.add_parser("dtdata",help="Update employee table")
    #parser_uptbemp.add_argument("tb",help="give table name",action='store')
    parser_uptbemp.add_argument("id",help="give table name",action='store')
    parser_uptbemp.add_argument("date",help="give table name",action='store',type=str)

       
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



def delete_data(args):
     db_uri = f"postgresql:///{args.dbname}"
     session = models.get_session(db_uri)
     query = (sa.delete(models.leaves)
              .where((models.leaves.empid == args.id)&
                     (models.leaves.date == args.date))
             )
     result = session.execute(query)
     rows_deleted = result.rowcount
     session.commit()
     if rows_deleted == 0:
       logger.error(f"No data found for id:-{args.id} date:-{args.date}")
     else:
       logger.info(f"Leave data for id:-{args.id} date:-{args.date} is deleted")
     



#Create details,leaves,designation table and add data to designation table
def create_table(args):
  try:
    db_uri = f"postgresql:///{args.dbname}"
    session = models.get_session(db_uri)
    engine = models.create_engine(db_uri)
    tables = ['employee','leaves','designation']
    for table in tables:
      table_exists = engine.dialect.has_table(engine.connect(), table , schema='public')

    if table_exists:
       logger.error(f"All tables exists")
    else:
      models.create_all(db_uri)
      designations = [models.designation(title="Staff Engineer", max_leaves=20),
                      models.designation(title="Senior Engineer", max_leaves=18),
                      models.designation(title="Junior Engineer", max_leaves=12),
                      models.designation(title="Technical Lead", max_leaves=12),
                      models.designation(title="Project Manager", max_leaves=15)]
      session.add_all(designations)
      session.commit()
      logger.info("Tables created successfully")
  except (sa.exc.OperationalError,pg.OperationalError) as e:
    raise HRException(e)



#Details table alteration starts


  
#Insert data into details table from csv 
def add_data_to_table_details(args):
  db_uri = f"postgresql:///{args.dbname}"
  session = models.get_session(db_uri)
  try:
    with open(args.file,'r') as f:
      reader = csv.reader(f)
      for last_name,first_name,title,email,phone in reader:
        q = sa.select(models.designation).where(models.designation.title==title)
        designation = session.execute(q).scalar_one()
        employee = models.employee(lastname=last_name,firstname=first_name,title=designation,email=email,ph_no=phone)
        logger.debug("Inserted data of %s",email)
        session.add(employee)
      session.commit()
    logger.info("data inserted into details table")
  except (pg.errors.UniqueViolation,sa.exc.IntegrityError) as e:
    raise HRException("data provided already exists in table employee")

 
 
 
# fetchone we get details in a tupule fetchall we get details in a tupule which is present inside a list      
#Genereate vcard,qrcode for a single employee and also show vcard info on terminal
def retriving_data_from_database(args):
  db_uri = f"postgresql:///{args.dbname}"
  session = models.get_session(db_uri)
  try:
    query =  ( sa.select
               (models.employee.lastname,
                models.employee.firstname,
                models.designation.title,
                models.employee.email,
                models.employee.ph_no)
               .where(models.employee.title_id==models.designation.jobid,
                      models.employee.empid==args.id)
              )
    x=session.execute(query).fetchall()
    session.commit()
    if x != []:
      for lastname,firstname,title,email,phone_number in x:
        print(f"""Name        : {firstname} {lastname}
Designation : {title}
Email       : {email}
Phone       : {phone_number}""")
        if args.vcard:
           print("\n",implement_vcf(lastname,firstname,title,email,phone_number))
           logger.debug(lastname,firstname,title,email,phone_number)
        if args.vcf:
          if not os.path.exists('worker_vcf'):
            os.mkdir('worker_vcf') 
          imp_vcard = implement_vcf(lastname,firstname,title,email,phone_number)
          with open(f'worker_vcf/{email}.vcf','w') as j:
             j.write(imp_vcard)
             logger.debug(f"Done generating vcard for {email}")
          logger.info(f"Done generating vcard of {email}")
        if args.qrcd:
           if not os.path.exists('worker_vcf'):
             os.mkdir('worker_vcf')
           imp_qrcode = implement_qrcode(lastname,firstname,title,email,phone_number)
           with open(f'worker_vcf/{email}.qr.png','wb') as f:
              f.write(imp_qrcode)
              logger.debug(f"Done generating qrcode for {email}")
           logger.info(f"Done generating qrcode of {email}")
    else:
      logger.error(f"Employee with id {args.id} not found")
  except Exception as e:
    logger.error("Employee with id %s not found",args.id)


#Generate vcard and qrcode for given number of employees
def genrate_vcard_file(args):
  db_uri = f"postgresql:///{args.dbname}"
  session = models.get_session(db_uri)
  if not os.path.exists('worker_vcf'):
    os.mkdir('worker_vcf')
  count = 1
  try:
    query = (sa.select
             (models.employee.lastname,
              models.employee.firstname,
              models.designation.title,
              models.employee.email,
              models.employee.ph_no)
             .where(models.employee.title_id==models.designation.jobid)
             )
    data = session.execute(query).fetchall()
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
             logger.debug(f"Generating qrcode for {email}")
             with open(f'worker_vcf/{email}.qr.png','wb') as f:
               f.write(imp_qrcode)
      logger.info(f"Done generating qrcode of {email}")
    logger.info(f"Done generating vCards for {args.number} employees") 
  except IndexError as e:
    raise HRException ("number of employee out of boundary")

#Insert data into table leaves
def add_data_to_leaves_table(args):
  db_uri = f"postgresql:///{args.dbname}"
  session = models.get_session(db_uri)
  try:
    insert_info = (models.leaves(empid=args.employee_id,date=args.date,reason=args.reason))
    session.add(insert_info)
    session.commit()
    logger.info("data inserted to leaves table")
  except (pg.errors.UniqueViolation,sa.exc.IntegrityError) as e:
      raise HRException (e)


  

#retrieve number of leaves remaining for an employee (single employee)
def retrive_data_from_new_table(args):
  db_uri = f"postgresql:///{args.dbname}"
  session = models.get_session(db_uri)
  try:
    rtr_count = (
                 sa.select
                    (sa.func.count(models.employee.empid),
                    models.employee.firstname,
                    models.employee.lastname,
                    models.designation.title,
                    models.employee.email,
                    models.designation.max_leaves
                    )
                    .where(models.employee.empid==args.employee_id,
                           models.designation.jobid==models.employee.title_id,
                           models.leaves.empid==models.employee.empid)
                    .group_by(models.employee.empid,
                              models.designation.title,
                              models.designation.max_leaves)
                  )

    data = session.execute(rtr_count).fetchall()
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
    if data == []:
       query = (
                sa.select
                (models.designation.max_leaves,
                models.employee.firstname,
                models.employee.lastname,
                models.employee.email,
                models.designation.title
                )
                .where(models.employee.empid == args.employee_id,
                       models.designation.jobid==models.employee.title_id)
                )
       leaves = session.execute(query).fetchall()
       for num_of_leaves,firstname,lastname,email,designation in leaves:
         d = f"""Name of employee : {firstname} {lastname}
Email : {email}
Designation : {designation}
Maximum alloted leaves : {num_of_leaves}
Available leaves : {num_of_leaves}
Total leaves taken : 0"""
       print(d) 
  except UnboundLocalError as e:
    raise HRException ("provided employee id is not in tables")

#Generate details of employees leaves on csv file
def generate_leave_csv(args):
  db_uri = f"postgresql:///{args.dbname}"
  session = models.get_session(db_uri)
  with open(f"{args.filename}.csv","w") as f:
    data = csv.writer(f)
    a = "Employee_id","firstname","lastname","email","title","Total number of leaves","Leaves left"
    data.writerow(a)
  f.close()
  query0 = (
            sa.select
            (sa.func.count(models.employee.empid))
            )
  x = session.execute(query0).fetchall()
  for i in x:
    for j in i:
      count = j
  for i in range (1,count+1):
    query1 = (
              sa.select(models.leaves.empid)
              .join(models.employee,models.employee.empid==models.leaves.empid)
              .where(models.employee.empid==i)
             )
    data = (session.execute(query1).fetchall())
    if data == []:
      query2 = (
                sa.select
                (models.employee.empid,
                 models.employee.firstname,
                 models.employee.lastname,
                 models.employee.email,
                 models.designation.title,
                 models.designation.max_leaves
                )
                .where(models.employee.empid == i,
                       models.employee.title_id == models.designation.jobid)
                )
      n = session.execute(query2).fetchall()
      for serial_number,firstname,lastname,email,title,num_of_leaves in n:
        with open(f"{args.filename}.csv","a") as f:
          data = csv.writer(f)
          a = serial_number,firstname,lastname,email,title,num_of_leaves,num_of_leaves
          data.writerow(a)
        f.close()
    else:
      query3 = (
                sa.select
                (models.employee.empid,
                 models.employee.firstname,
                 models.employee.lastname,
                 models.employee.email,
                 models.designation.title,
                 models.designation.max_leaves
                )
                .where(models.employee.empid == i,
                       models.employee.title_id == models.designation.jobid)
                )
      n = session.execute(query3).fetchall()
      for serial_number,firstname,lastname,email,title,num_of_leaves in n:
        num_leaves = num_of_leaves
      query4 = (
                sa.select
                          (sa.func.count(models.leaves.empid),
                          models.leaves.empid)
                          .where(models.leaves.empid==i)
                          .group_by(models.leaves.empid)
               )
      m = session.execute(query4).fetchall()
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
  logger.info(f"CSV file {args.filename}.csv consisting of employee's leave data is generated") 
  
  
# Database implementation ends

#web implementaion starts

def implementing_web(args):
    web.app.config["SQLALCHEMY_DATABASE_URI"] = f"postgresql:///{args.dbname}"
    web.db.init_app(web.app)
    web.app.run()  

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
    operations = { "initdb"   : create_table,
                   "import"   : add_data_to_table_details,
                   "empinfo"  : retriving_data_from_database,
                   "genvcard" : genrate_vcard_file,
                   "initlv"   : add_data_to_leaves_table,
                   "emplv"    : retrive_data_from_new_table,
                   "leavecsv" : generate_leave_csv,
                   "dtdata"   : delete_data,
                   "web"      : implementing_web
                 }
    operations[args.subcommand](args)

  except HRException as e:
     logger.error("Program aborted due to %s", e)
     sys.exit(-1)
     
if __name__ == '__main__':
   main()    
   
   
   

