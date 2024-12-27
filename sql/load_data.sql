LOAD DATA local infile '~/desktop/hong/dbms/final/PS.csv' 
INTO TABLE ps
FIELDS TERMINATED BY ',' 
LINES TERMINATED BY '\n' 
IGNORE 2 LINES; 