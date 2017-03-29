#// SEESUN CRM //

###### Developed by Team UBQAI -- You Ling, Li Fuyuan, Teng Wei, Cai Chang, Li Yixiao

### VERSION 1.0 , Feb-7-2017 


#### How to run the project

	1. install python3.5.3

	2. install all extensions listed in requirements.txt
		$ pip install -r requirements.txt

	3. run the project
		$ python main.py
		OR
		$ python manage.py runserver

#### About database

	1. Default database: Postgresql

	2. Database is supposed to be initialized after installed and configured at the first time
		$ python manage.py db init

	3. Data migration related
		Firstly, create a migration file, with upgrade and rollback function
		$ python manage.py db migrate
		Secondly, execute migration file and update database
		$ python manage.py db upgrade
		And you can rollback your last migration if necessary
		$ python manage.py db downgrade
		IF database conflict example:  Multiple heads are present for given argument 'head'; f96e60b9c39c, 636191448952
		$ python manage.py db merge -m "merge migration conflict" f96e60b9c39c  636191448952

	4. Execute seed file to create a bunch of sample data
		$ python seed.py

#### Testing

	$ python manage.py test

#### Console

	$ python manage.py shell
