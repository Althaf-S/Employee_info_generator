import csv
import genvcf

#def test_details_from_csv():

#test_details_from_csv()


def test_details_from_csv():
  result = genvcf.details_from_csv('test.csv')
  assert result == [['Lopez', 'Kathy', 'Horticulturist, amenity', 'kathy.lopez@warren.org', '001-383-311-4585'], 
                    ['Lawson', 'Kristy', 'Quantity surveyor', 'krist.lawso@brown-robinson.com', '372.280.1290']]
                    
def test_generate_vcs():
  names = [['Lopez', 'Kathy', 'Horticulturist, amenity', 'kathy.lopez@warren.org', '001-383-311-4585']]
  genvcf.generate_vcs(names)
  with open('worker_vcf/kathy.lopez@warren.org.vcf','r',newline='') as f:
       vcard = f.read()
       assert f"""BEGIN:VCARD
VERSION:2.1
N:Kathy;Lopez
FN:Lopez Kathy
ORG:Authors, Inc.
TITLE:Horticulturist, amenity
TEL;WORK;VOICE:001-383-311-4585
ADR;WORK:;;100 Flat Grape Dr.;Fresno;CA;95555;United States of America
EMAIL;PREF;INTERNET:kathy.lopez@warren.org
REV:20150922T195243Z
END:VCARD
"""                    in vcard 
def csv_test_data():
   names = [['Lopez', 'Kathy', 'Horticulturist, amenity', 'kathy.lopez@warren.org', '001-383-311-4585'], 
             ['Lawson', 'Kristy', 'Quantity surveyor', 'krist.lawso@brown-robinson.com', '372.280.1290']]
  # print(names)
   with open('test.csv', 'w', newline='') as csvfile:
     writer = csv.writer(csvfile)
     for i in names:
       writer.writerow(i)
   return csvfile



 


