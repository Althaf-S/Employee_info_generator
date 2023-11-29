#OBJECTIVE

- Generate vcard qrcode and employee leave data for a list of employees whose details are provided in a CSV file.

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
            
#EXECUTION

- Database to which the data needs to be added should be created manually (postgres is used for databse manipulations).

- The program needs to be executed from command line. The CSV file from which the data needs to be extracted should be provided as command line argument when needed to load the data.

- Format for providing command line argument and running file is 
          
        python3 <program_file_name> <arguments>.

- Data will be generated on the folder specified in the program and the direcory to store and data will be created in the folder which the user use for execution of program.

- Execution of arguments
 
-- Log file is where all the data regarding the execution of file is stored which includes the log in the format provided below
         [DEBUG] 2023-11-15 15:40:56,104 | genvcf.py:37 | Writing row 15 
   the above is an example of debug log information of the vCard generation.
   
-- The command provided below will help regarding what this program is used for and information regarding all its other arguments.
          python3 <program_file_name> -h/--help 

-- The command provided below will print the debug log data in the terminal showing the debug log data for all the file generated. Running without -v/--verbos will show you       information regarding whether the files are generated or not.
          python3 <program_file_name> -v/--verbose 
          
-- By default a database name will be present in parser, this default database name is the name provided on config.ini to change this to another default database name just use this argument if theuser needs to add a new database name use this subparser command to do the same. Or else you can use the default database.
          python3 <program_file_name> -d/--dbname



