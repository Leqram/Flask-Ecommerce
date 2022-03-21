from flask import Flask


app = Flask(__name__, static_url_path="/static", static_folder='D:/Project/Project P/Belajar/Bidyshop/static')
# app.secret_key = b'\xf7N\xca\x19\xb1\xb7|3'