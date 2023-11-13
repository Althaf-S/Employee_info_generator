import csv
import faker
import sys

def main():
    f = faker.Faker()
    names = []
    for i in range(100):
        record = []
        lname = f.last_name()
        fname = f.first_name()
        domain = f.domain_name()
        designation = f.job()
        email = f"{fname[:5].lower()}.{lname[:5].lower()}@{domain}"
        phone = f.phone_number()
        record = [lname, fname, designation, email, phone]
        names.append(record)
        print (record)
    return names
#csv
def write_in_csv(filename,data):
   with open(filename, 'w', newline='') as csvfile:
     writer = csv.writer(csvfile)
     for i in data:
       writer.writerow(i)
   return  csvfile    
  


if __name__ == "__main__":
    data = main()
    csv_file  = sys.argv[1]
    write_in_csv(csv_file,data)
