from app import app
from flask_mysqldb import MySQL

mysql = MySQL(app)

# configure MySQL
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = ''
app.config['MYSQL_DB'] = 'e_commerce'
app.config['MYSQL_HOST'] = 'localhost'


