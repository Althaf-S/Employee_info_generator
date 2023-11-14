import csv
import os
import requests
import sys

def details_from_csv(csvfile):
  data = []
  with open(csvfile,'r') as f:
    reader = csv.reader(f)
    for item in reader:
      data.append(item)
  return data


def generate_vcf(details):
  if not os.path.exists('worker_vcf'):
    os.mkdir('worker_vcf')
  for first_name,last_name,job,email,ph_no in details:
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

def generate_qrcode(details):
  for first_name,last_name,job,email,ph_no in details:
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

  
  
def main():
  file_name = sys.argv[1]
  details = details_from_csv(file_name)
  generate_vcf(details)
  generate_qrcode(details)

if __name__ == "__main__":
  main()
