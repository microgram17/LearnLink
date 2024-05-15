# LearnLink
Platform for finding study resources online.
https://microgram.pythonanywhere.com/


## Database setup and migration
Both locally and on pythonanywhere
1. Initialize database
```
flask db init
```
2. Run Flask migrations
```
flask db migrate
```
3. Run flask db upgrade
```
flask db upgrade
```
4. Check if tables have been created correctly moving to the directory where .db file is located. Typically in side of instance\
```
cd instance\
```
5. Open sqlite3 shell and the .db file
```
sqlite3 learnlink.db
```
6. display database shcema and check tables
```
.schema
```


### when run locally 
Run flask app
```
py app.py
```

### error fixes
if you get error
ModuleNotFoundError: No module named 'pkg_resources'
run this command
```
pip install setuptools
```
