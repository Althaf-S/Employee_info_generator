import csv
import logging
import argparse
import os
import requests
import sys

logger = None

def details_from_csv(csvfile):
  data = []
  with open(csvfile,'r') as f:
    reader = csv.reader(f)
    for item in reader:
      data.append(item)
  return data

def parse_args():
    parser = argparse.ArgumentParser(prog="genvcf.py", description="Generates sample employee database as csv")
    parser.add_argument("ipfile", help="Name of output csv file")
    parser.add_argument("-v", "--verbose", help="Print detailed logging", action='store_true', default=False)
    parser.add_argument("-n", "--number", help="Number of records to generate", action='store', type=int, default=100)
    args = parser.parse_args()
    return args

def implement_log(log_level):
    global logger
    logger = logging.getLogger("genvcf_log")
    handler = logging.StreamHandler()
    fhandler = logging.FileHandler("run.log")
    fhandler.setLevel(logging.DEBUG)
    handler.setLevel(log_level)
    handler.setFormatter(logging.Formatter("[%(levelname)s] %(asctime)s | %(filename)s:%(lineno)d | %(message)s"))
    fhandler.setFormatter(logging.Formatter("[%(levelname)s] %(asctime)s | %(filename)s:%(lineno)d | %(message)s"))
    logger.setLevel(logging.DEBUG)
    logger.addHandler(handler)
    logger.addHandler(fhandler)


def data_from_details(details,number):
  data = []
  for i in range(0,number):
     data.append(details[i])
  return data


def generate_vcf(data):
  if not os.path.exists('worker_vcf'):
    os.mkdir('worker_vcf')
  count = 1
  for first_name,last_name,job,email,ph_no in data:
       logger.debug("Writing row %d", count)
       count +=1
       with open(f'worker_vcf/{email}.vcf','w') as j:
          j.write(f"""
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
""")
  logger.info("Done generating vCards")  
       
def generate_qrcode(data):
  count = 1
  for first_name,last_name,job,email,ph_no in data:
    logger.debug("Writing row %d", count)
    count +=1
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
    with open(f'worker_vcf/{email}.qr.png','wb') as f:
      f.write(reqs.content)
  logger.info("Done generating qr code files")
  
  
def main():
  #file_name = sys.argv[1]
  #log_level = sys.argv[2]
  args = parse_args()
  if args.verbose:
     implement_log(logging.DEBUG)
  else:
     implement_log(logging.INFO)
  
  details = details_from_csv(args.ipfile)
  data = data_from_details(details,args.number)
  generate_vcf(data)
  generate_qrcode(data)

if __name__ == "__main__":
  main()
