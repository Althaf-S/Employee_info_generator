# OBJECTIVE

- Generate vcard qrcode and employee leave data for a list of employees whose details are provided in a CSV file.

# INPUT
- The file from whichnthe whole backend runs is genvcf.py do while trying to run the application's backend use 

        python3 genvcf.py <args>

- CSV file from which data is extracted needs to be provided as command line argument to load data.

- General format of data provided in CSV file is given below;
    [last_name, first_name, job, email_address, phone_number]
    
    Example of data written in this format will be like this:
    
      Morgan, Melinda, Advertising Copywriter, melin.morga@smith_write.com, +71-(391)-2934
      
# OUTPUT

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
            
# EXECUTION

- Database to which the data needs to be added should be created manually (postgres is used for databse manipulations).

- The program needs to be executed from command line. The CSV file from which the data needs to be extracted should be provided as command line argument when needed to load the data.

- Format for providing command line argument and running file is 
          
        python3 <program_file_name> <arguments>.

- Data will be generated on the folder specified in the program and the direcory to store and data will be created in the folder which the user use for execution of program.

## Execution of arguments

- To  start localhost:5000 i.e; our backend server we need to use command
  
         python3 <program_file_name> web
 
- To get debug information use the following command.

         python3 <program_file_name> -v/--verbose
   
- The command provided below will help regarding what this program is used for and information regarding all its other arguments.

         python3 <program_file_name> -h/--help

- The command provided below will print the debug log data in the terminal showing the debug log data for all the file generated. Running without -v/--verbos will show you       information regarding whether the files are generated or not.

         python3 <program_file_name> -v/--verbose
          
- By default a database name will be present in parser, this default database name is the name provided on config.ini to change this to another default database name just use this argument if theuser needs to add a new database name use this subparser command to do the same. Or else you can use the default database.

         python3 <program_file_name> -d/--dbname
      
- This command is used to create the database tables that are needed to store the data. The query for creation of tables is obtained from a file init.sql. Also data for designation table is inserted through this command.

         python3 <program_file_name> initdb
      
- import command is used to load data to database tables and file command along with load command is used to add csv file name from which data is loaded to database.

         python3 <program_file_name> import file
      
- empinfo is used to retrieve data of a particular employee and all other subcommands are optional --vcard is used to show the vcard details of user in terminal, id should be used to get the details of thet particular employee and this id is ther employee-id , --vcf is used to generate vcard for that particular employee, --qrcd is used to generate qrcode for that employee.

         python3 <program_file_name> empinfo id --vcard --vcf --qrcd
      
- genvcard is user to generate vcard for a particular number of employee, -n/--number is used to generate that much number of employee's vcards, --qrcd is used to generate qrcode for given number of employees. By default this number is set as 10.

         python3 <program_file_name> genvcard -n/--number --qrcd
      
- initlv is used to insert data to leaves table. 'date' is the date in which employee was leave. employee_id is the id of employee from details table reason is the cause of leave. 

         python3 <program_file_name> initlv date employee_id reason
      
- emplv command is used to retrieve leaves data regarding an employee by providing employee_id after typing rtrlv, the data will be shown on terminal.

         python3 <program_file_name> emplv employee_id
      
- leavecsv command is to get details of leaves of each employee on a csv file and -f is a subcommand that can be used to provide csv filename without the file extention bydefault a filename is set 'lv.csv'.
 
         python3 <program_file_name> leavecsv -f










