#OBJECTIVE

Generate vcard qrcode and employee leave data for a list of employees whose details are provided in a CSV file.

#INPUT

- CSV file from which data is extracted needs to be provided as command line argument to load data.

- General format of data provided in CSV file is given below;
    [last_name, first_name, job, email_address, phone_number]
    
    Example of data written in this format will be like this:
    
      Morgan, Melinda, Advertising Copywriter, melin.morga@smith_write.com, +71-(391)-2934
      
#OUTPUT

- There will be two output one is the vCard file for each employee and the other is a qr code .png format file which can be scanned using a mobile phone camera to get the data regarding an employee.
        
- qr code data is the same data witten in vCard file format and is generated for each employee. Name of both vCard and qr code files will be the mail-id of employer.

- Data inside a simple vCard file is of this format:
        
            BEGIN:VCARD
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
            
- Output of the data regarding leaves generated on screen example:

            Name of employee : Anne Smith
            Email : smithanne@outlook.com
            Designation : Staff Engineer
            Maximum alloted leaves : 20
            Available leaves = 15 
            

