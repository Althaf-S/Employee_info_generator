CREATE TABLE details (serial_number SERIAL PRIMARY KEY, lastname VARCHAR(50),firstname VARCHAR(50),title VARCHAR(200),email VARCHAR(150),phone_number VARCHAR(50));

CREATE TABLE leaves (serial_number SERIAL PRIMARY KEY,date DATE,employee_id INTEGER REFERENCES details(serial_number),reason VARCHAR(50),UNIQUE (date,employee_id));
