import csv
import os
import sys

def details_from_csv(csvfile):
  data = []
  with open(csvfile,'r') as f:
    reader = csv.reader(f)
    for item in reader:
      data.append(item)
  return data
 
def generate_vcs(details):
  for man in details:
    first_name = man[0]
    last_name = man[1]
    job = man[2]
    email = man[3]
    ph_no = man[4]
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
      

def main():
  file_name = sys.argv[1]
  details = details_from_csv(file_name)
  generate_vcs(details)
  

if __name__ == "__main__":
  main()
