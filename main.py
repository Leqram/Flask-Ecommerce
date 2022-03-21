from app import app
from db_config import mysql
from functools import wraps
from passlib.hash import sha256_crypt

from werkzeug.utils import secure_filename
from werkzeug.security import check_password_hash, generate_password_hash
from flask import Flask, redirect, render_template, flash, make_response, url_for, request, session, jsonify
from midtransclient import Snap, CoreApi


import midtransclient
import MySQLdb.cursors
import pdfkit

import json
import os
import re
import datetime




SERVER_KEY = 'SB-Mid-server-6esF5nrYh4dHdBcCEaQRB1V4'
CLIENT_KEY = 'SB-Mid-client-4gQWc5UKitTkbJvB' 

core = CoreApi(
    is_production=False,
    server_key = SERVER_KEY,
    client_key = CLIENT_KEY
)


app.config['UPLOAD_FOLDER'] = 'D:/Project/Project P/Belajar/Bidyshop/static/assets/images/'
ALLOWED_EXTENSIONS = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'}

app.secret_key = "susu ultramilk"





def format_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS



def is_logged_in(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        if 'loggedin' in session:
            return f(*args, *kwargs)
        else:
            return redirect(url_for('login'))

    return wrap


def not_logged_in(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        if 'loggedin' in session:
            return redirect(url_for('index'))
        else:
            return f(*args, *kwargs)

    return wrap

 
def wrappers(func, *args, **kwargs):
    def wrapped():
        return func(*args, **kwargs)

    return wrapped


def array_merge( first_array , second_array ):
    if isinstance( first_array , list ) and isinstance( second_array , list ):
    	return first_array + second_array
    elif isinstance( first_array , dict ) and isinstance( second_array , dict ):
    	return dict( list( first_array.items() ) + list( second_array.items() ) )
    elif isinstance( first_array , set ) and isinstance( second_array , set ):
    	return first_array.union( second_array )
    return False




@app.route('/convert')
def convert_html_to_pdf():
    path_wkhtmltopdf = "D:/Program/wkhtmltopdf/bin/wkhtmltopdf.exe"
    config = pdfkit.configuration(wkhtmltopdf = path_wkhtmltopdf)
    pdfkit.from_url("http://localhost:5000/operator_penjualan/", "data_penjualan.pdf", configuration = config)
    return redirect(url_for('penjualan'))






@app.route('/', methods = ['GET', 'POST'])
def index():
    cur = mysql.connection.cursor()
    values = 'Tshirt'
    cur.execute("SELECT * FROM barang WHERE kategori = %s ORDER BY RAND() LIMIT 2", (values,))
    tshirt = cur.fetchall()
    values = 'Tas'
    cur.execute("SELECT * FROM barang WHERE kategori = %s ORDER BY RAND() LIMIT 2", (values,))
    Tas = cur.fetchall()
    values = 'Watch'
    cur.execute("SELECT * FROM barang WHERE kategori = %s ORDER BY RAND() LIMIT 2", (values,))
    Watch = cur.fetchall()
    values = 'Kemeja'
    cur.execute("SELECT * FROM barang WHERE kategori = %s ORDER BY RAND() LIMIT 1", (values,))
    Kemeja = cur.fetchall()

    username = 'username' in session
    cur.execute("SELECT * FROM user WHERE username = %s", (username,))
    profiles = cur.fetchall()

    if request.method == "POST" and 'search' in request.form:
        search = request.form['search']
        cur.execute("SELECT * FROM barang WHERE nama_barang LIKE %s", ("%{}%".format(search),))
        searching = cur.fetchall()
        return render_template('index_new.html', searching = searching)

    cur.close()
    return render_template('index_new.html', tshirt = tshirt, Tas = Tas, Watch = Watch, Kemeja = Kemeja, profiles = profiles)





@app.route('/product_details', methods = ["GET", "POST"])
def product_details():
    cur = mysql.connection.cursor()
    if 'view' in request.args:
        id_barang = request.args['view']
        cur.execute("SELECT * FROM barang WHERE id_barang = %s", (id_barang,))
        produk = cur.fetchall()

        cur.execute("SELECT * FROM barang WHERE id_barang = %s", (id_barang,))
        row = cur.fetchone()

        kategori = row[6]
        view = row[8]
        cur.execute("UPDATE barang SET view = %s + 1 WHERE id_barang = %s", (view, id_barang,))
        mysql.connection.commit()
        
        cur.execute("SELECT * FROM barang WHERE kategori = %s ORDER BY view DESC LIMIT 4", (kategori,))
        recom_produk = cur.fetchall()

        # if produk:
        #     session['id_barang'] = produk[0]
        #     print(session['id_barang'])
        #     return redirect(url_for('cart'))
        return render_template('detail_product.html', produks = produk, recom_produk = recom_produk)
    if request.method == 'POST' and 'quantity' in request.form:
        quantity = request.form['quantity']
        print("barang yang dipesan sebanyak " + quantity)
        return redirect(url_for('cart'))

    return render_template('detail_product.html')



# @app.route('/cart', methods = ['POST', 'GET'])
# def cart():
#     _quantity = request.args.get('quantity')
#     if 'cart' in request.args:
#         _id = request.args['cart']
#         cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
#         cur.execute("SELECT * FROM barang WHERE id_barang = %s", (_id,))
#         rows = cur.fetchone()

#         itemArray = {'id_barang' : rows[0],'nama_produk' : rows[1], 'quantity' : [_quantity], 'price' : rows[2], 'subtotal' : _quantity * rows[2]}
#         all_total_price = 0
#         all_total_quantity = 0

#         session.modified = True
#         if 'cart item' in session:
#             if rows['id_barang'] in session['cart_item']:
#                 for key, value in session['cart_item'].items():
#                     if rows['id_barang'] == key:
#                         old_quantity = session['cart_item'][key]['quantity']
#                         total_quantity = old_quantity + _quantity
#                         session['cart_item'][key]['quantity'] = total_quantity
#                         session['cart_item'][key]['total_price'] = total_quantity * rows[2]
            
#             else:
#                 session['cart_item'] = array_merge(session['cart_item'], itemArray)

#             for key, value in session['cart_item'].items():
#                 individual_quantity = int(session['cart_item'][key]['quantity'])
#                 individual_price = float(session['cart_item'][key]['total_price'])
#                 all_total_quantity = all_total_quantity + individual_quantity
#                 all_total_price = all_total_price + individual_price
        
#         else:
#             session['cart_item'] = itemArray
#             all_total_quantity = all_total_quantity + _quantity
#             all_total_price = all_total_price + _quantity * rows[2]
            
#         session['all_total_quantity'] = all_total_quantity
#         session['all_total_price'] = all_total_price


#     return render_template('cart.html')


# code pada function cart salah seharusnya
# code tersebut berada di product details
# cart hanya menerima data dan menampilkannya




@app.route('/cart')
def cart():
    cur = mysql.connection.cursor()
    if 'cart' in request.args:
        id_barang = request.args['cart']
        cur.execute("SELECT * FROM barang WHERE id_barang = %s", (id_barang,))
        produk = cur.fetchall()
        try:
            if session['loggedin'] == True:
                print(session['uid'])
        except Exception as e:
            print(e)
    return render_template('cart.html', produks = produk)






@app.route('/address', methods = ['GET', 'POST'])
@is_logged_in
def address():
    cur = mysql.connection.cursor()
    if 'cid' in request.args:
        try:
            id_barang = request.args['cid']
            cur.execute("SELECT * FROM barang WHERE id_barang = %s", (id_barang,))
            barang = cur.fetchall()
            uid = session['uid']
            cur.execute("SELECT * FROM user WHERE uid = %s", (uid,))
            user = cur.fetchall()
            return render_template('address.html', data_barang = barang, data_user = user)
        except Exception as e:
            print(e)

    if request.method == "POST":
        nama_barang = request.form['nama_barang']
        username = request.form['username']
        penerima = request.form['penerima']
        alamat = request.form['alamat']
        kota = request.form['kota']
        no_telepon = request.form['no_telepon']
        print('bautabsasda')
        kode_pos = request.form['kode_pos']
        timestamp = datetime.datetime.now()
        now_time = timestamp.strftime("%y-%m-%d %H:%M")
        

        cur.execute("INSERT INTO pemesanan VALUES (NULL, %s, %s, %s, %s, %s, %s, %s, NULL, %s)", (nama_barang, username, penerima, alamat, kota, no_telepon, kode_pos, now_time))
        mysql.connection.commit()
        return redirect(url_for('invoice'))
        

    return render_template('address.html')


    

    
@app.route('/invoice', methods = ["GET", "POST"])
def invoice():
    snap = Snap(
        is_production=False,
        server_key=SERVER_KEY,
        client_key=CLIENT_KEY
    )

    # no_pemesanan = session['id_pengiriman']
    timestamp = datetime.datetime.now()
    hari = datetime.timedelta(hours=24)
    now_time = timestamp.strftime("%y-%m-%d %H:%M")
    time = timestamp.strftime("%y%m%d%M")

    berlaku_sampai = timestamp + hari
    expired = berlaku_sampai.strftime("%y-%m-%d %H:%M")
    print(now_time)

    cur = mysql.connection.cursor()
    cur.execute('SELECT * FROM pemesanan WHERE now_time = %s', (now_time,))
    data_pemesanan = cur.fetchall()
    
    cur.execute('SELECT * FROM pemesanan WHERE now_time = %s', (now_time,))
    row = cur.fetchone()
    
    if row:
        nama_barang = row[1]
        kota = row[5]
        uid = session['uid']
        order_id = str(uid) + str(row[0])

        session['alamat'] = row[4]
        session['kota'] = row[5]
        session['kode_pos'] = row[7]

        cur.execute('SELECT * FROM barang WHERE nama_barang = %s', (nama_barang,))
        row_barang = cur.fetchone()
        harga = row_barang[2]

        cur.execute('SELECT * FROM kota where kota = %s', (kota,))
        row_kota = cur.fetchone()

        cur.execute('SELECT * FROM user where uid = %s', (uid,))
        row_user = cur.fetchone()

        cur.execute('SELECT * FROM barang WHERE nama_barang = %s', (nama_barang,))
        data_barang = cur.fetchall()

        berat_barang = row_barang[4]
        jarak = row_kota[2]
        print(berat_barang + jarak)

        
        
        if berat_barang <= 500:
            x = 6000
        if berat_barang <= 1000:
            x = 12000
        if berat_barang >= 2000:
            x = 18000
        if berat_barang >= 5000:
            x = 36000

        if jarak <= 5:
            y = 3000
        if jarak >= 10:
            y = 6000
        if jarak >= 50:
            y = 30000
        sum = x + y
        total = harga + sum

        transaksi_token = snap.create_transaction({ 
            "transaction_details": {
                "order_id": order_id + time,
                "gross_amount": total
            },
            "customer_details": {
                "first_name": row_user[3],
                "email": row_user[4],
                "phone": "+62 " + row_user[5]
            }
        })
        code_transaksi = order_id + time
        code_pengiriman = 'bidy' + str(row[7]) + time
        session['code_transaksi'] = code_transaksi
        username = session['username']
        
        penerima = row[3]
        no_telepon = row[6]
        

        cur.execute("INSERT INTO transaksi VALUES (%s, %s, %s, %s, %s, %s, %s, %s, NULL)", (code_transaksi, username, nama_barang, total, penerima, no_telepon, 'pending', 'sedang dikemas'))
        mysql.connection.commit()

        cur.execute("INSERT INTO pengiriman VALUES (%s, %s, %s, %s, %s, %s, %s)", (code_pengiriman ,code_transaksi, penerima, row[4], row[5], row[7], 'Pesanan sudah diterima',))
        mysql.connection.commit()


        return render_template('invoice.html', data_barang = data_barang, sum = sum, client_key = snap.api_config.client_key,
                                total = total, harga = harga, data = data_pemesanan, expired = expired, order_id = order_id,
                                token = transaksi_token)
        
        
    return render_template('invoice.html', data = data_pemesanan, expired = expired)




@app.route('/cek_status_transaksi', methods = ['GET', 'POST'])
def cek_status_transaksi():
    cur = mysql.connection.cursor()
    now_time = datetime.datetime.now().strftime("%y-%m-%d %H:%M")
    time = datetime.datetime.now().strftime("%y%m%d%M")

    cur.execute('SELECT * FROM pemesanan WHERE now_time = %s', (now_time,))
    row = cur.fetchone()

    uid = session['uid']
    order_id = "#" + str(uid) + str(row[0])
    code_transaksi = order_id + time

    request_json = request.get_json()
    transaction_status = core.transactions.status(request_json['transaction_id'])

    if transaction_status == 'pending':
        cur.execute("UPDATE transaksi SET status_transaksi = %s WHERE code_transaksi = %s", ('pending', code_transaksi,))
        mysql.connection.commit()
        return redirect(url_for("status_pengiriman"))

    return jsonify(transaction_status)





@app.route('/status_pengiriman')
def status_pengiriman():
    if 'code_transaksi' in session:
        cur = mysql.connection.cursor()
        order_id = session['code_transaksi']
        now_time = datetime.datetime.now()
        hari = datetime.timedelta(days=3)

        time = now_time + hari
        estimate_time = time.strftime("%m-%d-%y")


        cur.execute("SELECT * FROM transaksi where code_transaksi = %s", (order_id,))
        row_transaksi = cur.fetchone()

        cur.execute("SELECT * FROM pengiriman where code_transaksi = %s", (order_id,))
        informasi = cur.fetchall()

        barang = row_transaksi[2]


        cur.execute("SELECT * FROM barang where nama_barang = %s", (barang,))
        data_barang = cur.fetchall()
    else:
        return render_template('tracking.html')

    return render_template('tracking.html', barang = barang, order_id = order_id, data_barang = data_barang, informasi = informasi, estimate_time = estimate_time)





@app.route('/validasi')
def validasi():
    if 'code_transaksi' in session:
        values = 'Sudah diterima'
        cur = mysql.connection.cursor()
        code_transaksi = session['code_transaksi']
        cur.execute('UPDATE pengiriman SET status_transaksi = %s WHERE code_transaksi = %s', (values, code_transaksi))
        mysql.connection.commit()
        return redirect(url_for('status_pengiriman'))





@app.route('/user/account', methods = ["GET", "POST"])
@is_logged_in
def account():
    if 'uid' in session:
        id_user = session['uid']
        cur = mysql.connection.cursor()
        cur.execute('SELECT * FROM user where uid = %s', (id_user,))
        data = cur.fetchall()

        if request.method == 'post':
            current_password = request.form['current_password']

            if current_password in request.form == data[3]:            
                new_password = request.form['new_password']
                repeat_password = request.form['repeat_password']

                if new_password == repeat_password:
                    cur.execute("UPDATE user SET password = %s WHERE uid = %s", (repeat_password, id_user,))
                    data_password = cur.fetchall()
                    return redirect(url_for('account'))
                else:
                    flash("Repeat password tidak sama dengan new password")
            else:
                flash("Anda siapa?")
        return render_template('account_settings.html', data = data)

    return render_template('account_settings.html')




@app.route('/login', methods = ['GET', 'POST'])
@not_logged_in
def login():
    if request.method == 'POST' and 'username' in request.form and 'password' in request.form:

        username = request.form['username']
        password = request.form['password']
        cursor = mysql.connection.cursor()
        cursor.execute("SELECT * FROM user WHERE username = %s AND password = %s", (username, password))
        user = cursor.fetchone()

        # login sesuai role
        try:
            if user[7] == "user":
                session['uid'] = user[0]
                session['username'] = user[1]
                session['password'] = user[2]
                session['nama'] = user[3]
                session['role'] = user[7]
                session['loggedin'] = True
                return redirect(url_for('index'))

            if user[7] == "kurir":
                session['uid'] = user[0]
                session['username'] = user[1]
                session['password'] = user[2]
                session['nama'] = user[3]
                session['role'] = user[7]
                session['loggedin'] = True
                return redirect(url_for('kurir'))

            if user[7] == "admin_barang":
                session['ID'] = user[0]
                session['nama'] = user[3]
                session['password'] = user[2]
                session['role'] = user[7]
                session['loggedin'] = True
                return redirect(url_for('admin_barang'))
            
            if user[7] == "admin_pengiriman":
                session['ID'] = user[0]
                session['nama'] = user[3]
                session['password'] = user[2]
                session['role'] = user[7]
                session['loggedin'] = True
                return redirect(url_for('admin_pengiriman'))

            if user[7] == "operator_transaksi":
                session['ID'] = user[0]
                session['nama'] = user[3]
                session['password'] = user[2]
                session['role'] = user[7]
                session['loggedin'] = True
                return redirect(url_for('data_transaksi'))

            if user[7] == "operator_penjualan":
                session['ID'] = user[0]
                session['nama'] = user[3]
                session['password'] = user[2]
                session['role'] = user[7]
                session['loggedin'] = True
                return redirect(url_for('penjualan'))

            if user[7] == "super":
                session['ID'] = user[0]
                session['nama'] = user[3]
                session['password'] = user[2]
                session['role'] = user[7]
                session['loggedin'] = True
                return redirect(url_for('admin'))

            
            

        except Exception as e:
            print(e)
        else:
            flash('Password atau username salah!!')

        return render_template('login/login.html', users = user)

    return render_template('login/login.html')


@app.route('/ForgotPassword?')
def forgot_password():
    return render_template('login/forgot.html')


@app.route('/logout')
def logout():
    session.pop('username', None)
    session.pop('nama', None)
    session.pop('uid', None)
    session.pop('ID', None)
    session.pop('role', None)
    session.pop('password', None)
    session.pop('loggedin', None)
    return redirect(url_for('index'))




@app.route('/register', methods = ['GET', 'POST'])
@not_logged_in
def register():
    error = ""
    if request.method == 'POST' and 'username' in request.form and 'password' in request.form and 'nama' in request.form and 'email' in request.form and 'no_telepon' in request.form and 'foto_profile' in request.files:

        username = request.form['username']
        password = request.form['password']
        nama = request.form['nama']
        email = request.form['email']
        no_telepon = request.form['no_telepon']
        profile = request.files['foto_profile']
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM user WHERE username = %s', (username,)) # memeriksa username pada DB
        user = cursor.fetchone()
        
        if user: 
            error = 'Username sudah dipakai!' # memeriksa apakah username sudah terpakai
        elif not re.match(r'[^@]+@[^@]+\.[^@]+', email): # regex email validation
            error = 'Email yang dimasukkan salah!'
        elif not re.match(r'[A-Za-z0-9]+', username): # regex username validation
            error = 'Username harus menggunakan huruf dan angka!'
        elif not username or not password or not email or not no_telepon:
            error = 'Ada form yang belum diisi!'
        else:
            cursor.execute('INSERT INTO user VALUES (NULL, %s, %s, %s, %s, %s, %s, %s)', (username, password, nama, email, no_telepon, profile, "user", ))
            mysql.connection.commit()
            error = 'Account berhasil dibuat'
            return redirect(url_for('login'))


    elif request.method == 'POST':
        error = 'Ada form yang belum diisi!'
    return render_template('login/register.html', error = error)





# Halaman kurir 
@app.route('/kurir')
def kurir():
    cur = mysql.connection.cursor()
    value = 'barang sedang dikemas'
    
    cur.execute("SELECT * FROM pengiriman WHERE status_transaksi = %s", (value,))
    data_pengiriman = cur.fetchall()

    cur.execute("SELECT * FROM pengiriman WHERE status_transaksi = %s", (value,))
    row_pengiriman = cur.fetchone()

    cur.execute("SELECT * FROM transaksi WHERE code_transaksi = %s", (row_pengiriman[1],))
    data_transaksi = cur.fetchall()

    cur.execute("SELECT * FROM transaksi WHERE code_transaksi = %s", (row_pengiriman[1],))
    row_transaksi = cur.fetchone()

    nama_barang = row_transaksi[2]
    print(nama_barang)
    cur.execute("SELECT * FROM barang WHERE nama_barang = %s", (nama_barang,))
    data_barang = cur.fetchall()
    
    nama = session['nama']
    
    return render_template('kurir/kurir.html', data_transaksi = data_transaksi, data_barang = data_barang, data_pengiriman = data_pengiriman,
                                                nama = nama)



# Detail pengiriman pada halaman kurir
@app.route('/details_pengiriman')
def details_pengiriman():
    cur = mysql.connection.cursor()
    if 'view_pengiriman' in request.args:
        code_transaksi = request.args['view_pengiriman']
        cur.execute("SELECT * FROM pengiriman WHERE code_transaksi = %s", (code_transaksi,))
        data_pengiriman = cur.fetchall()
        
        cur.execute("SELECT * FROM transaksi WHERE code_transaksi = %s", (code_transaksi,))
        data_transaksi = cur.fetchall()
        for row_barang in data_transaksi:
            nama_barang = row_barang[2]
        
        cur.execute("SELECT * FROM barang WHERE nama_barang = %s", (nama_barang,))
        data_barang = cur.fetchall()
        return render_template('kurir/details_pesanan.html', data_pengiriman = data_pengiriman, data_transaksi = data_transaksi, data_barang = data_barang)
    return render_template('kurir/details_pesanan.html')




@app.route('/admin/')
def admin():
    conn = mysql.connection
    cur = conn.cursor()
    cur.execute("SELECT * FROM barang")
    rows = cur.fetchall()
    return render_template('admin/item.html', rows = rows)




@app.route('/admin_barang/')
def admin_barang():
    conn = mysql.connection
    cur = conn.cursor()
    cur.execute("SELECT * FROM barang")
    rows = cur.fetchall()
    return render_template('admin/admin_barang.html', rows = rows)



@app.route('/user/management')
def management():
    conn = mysql.connection
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM user")
    rows = cursor.fetchall()
    return render_template('admin/users.html', rows = rows)





# Transaksi
@app.route('/data_transaksi')
def data_transaksi():
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM transaksi ORDER BY waktu_transaksi DESC")
    rows = cur.fetchall()
    return render_template('admin/data_transaksi.html', rows = rows)




@app.route('/transaksi_update', methods = ['POST'])
def update_transaksi():
    cur = mysql.connection.cursor()
    status_pembayaran = request.form['status_pembayaran']
    status_transaksi = request.form['status_transaksi']
    code_transaksi = request.form['code_transaksi']
    cur.execute("UPDATE transaksi SET status_pembayaran = %s, status_transaksi = %s WHERE code_transaksi = %s", (status_pembayaran, status_transaksi, code_transaksi,))
    mysql.connection.commit()
    return redirect(url_for('data_transaksi'))




@app.route('/delete/<int:code_transaksi>', methods = ['GET', 'POST'])
def delete_transaksi(code_transaksi):
    cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cur.execute("DELETE FROM transaksi WHERE code_transaksi = %s",(code_transaksi,))
    mysql.connection.commit()
    return redirect(url_for('data_transaksi'))

    


 
# penjualan
@app.route('/operator_penjualan/')
def penjualan():
    cur = mysql.connection.cursor()
    cur.execute(""" SELECT barang.nama_barang, barang.harga, barang.stok, barang.kategori, barang.view
    FROM barang INNER JOIN transaksi
    ON barang.nama_barang = transaksi.nama_barang
    WHERE transaksi.status_pembayaran = "berhasil"
    ORDER BY view desc """)
    data = cur.fetchall()
    return render_template('admin/data_penjualan.html', data = data)




# pengiriman
@app.route('/admin_pengiriman/')
def admin_pengiriman():
    conn = mysql.connection
    cur = conn.cursor()
    cur.execute("SELECT * FROM pengiriman")
    rows = cur.fetchall()
    return render_template('admin/data_jasa_pengiriman.html', rows = rows)




@app.route('/admin_pengiriman/update', methods = ['GET', 'POST'])
def update_pengiriman():
    status_transaksi = request.form['status_transaksi']
    code_pengiriman = request.form['code_pengiriman']
    cur = mysql.connection.cursor()
    cur.execute("UPDATE pengiriman SET status_transaksi = %s WHERE code_pengiriman = %s", (status_transaksi, code_pengiriman,))
    mysql.connection.commit()
    return redirect(url_for('admin_pengiriman'))



@app.route('/admin_pengiriman/<string:code_pengiriman>')
def delete_pengiriman(code_pengiriman):
    cur = mysql.connection.cursor()
    cur.execute("DELETE FROM pengiriman WHERE code_pengiriman = %s", (code_pengiriman))
    mysql.connection.commit()
    return redirect(url_for('admin_pengiriman'))



@app.route('/admin_pengiriman/kurir')
def data_kurir():
    value = "kurir"
    conn = mysql.connection
    cur = conn.cursor()
    cur.execute("SELECT * FROM user WHERE role = %s", (value,))
    rows = cur.fetchall()
    return render_template('admin/kurir.html', rows = rows)



@app.route('/admin_pengiriman/kota')
def kota():
    conn = mysql.connection
    cur = conn.cursor()
    cur.execute("SELECT * FROM kota")
    rows = cur.fetchall()
    return render_template('admin/kota.html', rows = rows)



@app.route('/kota/add', methods = ['GET', 'POST'])
def add_kota():
    if request.method == 'POST':
        id_kota = request.form['id_kota']
        kota = request.form['kota']
        jarak = request.form['jarak']
        
        if id_kota and kota and jarak:
            cur = mysql.connection.cursor()
            cur.execute("INSERT INTO kota VALUES (%s, %s, %s)", (id_kota, kota, jarak,))
            mysql.connection.commit()
            return redirect(url_for('kota'))
    return render_template('admin/add/add_kota.html')



@app.route('/admin_pengiriman/kota_update', methods = ['GET', 'POST'])
def update_kota():
    id_kota = request.form['id_kota']
    kota = request.form['kota']
    jarak = request.form['jarak']
    cur = mysql.connection.cursor()
    cur.execute("UPDATE kota SET kota = %s, jarak = %s WHERE id_kota = %s", (kota, jarak, id_kota,))
    mysql.connection.commit()
    return redirect(url_for('kota'))



@app.route('/admin_pengiriman/<int:id_kota>')
def delete_kota(id_kota):
    cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cur.execute("DELETE FROM kota WHERE id_kota = %s",(id_kota,))
    mysql.connection.commit()
    flash('Barang berhasil dihapus!')
    return redirect(url_for('kota'))





# add kurir lewat admin pengiriman
@app.route('/sign_up', methods = ['GET', 'POST'])
def sign_up():
    error = ""
    if request.method == 'POST' and 'username' in request.form and 'password' in request.form and 'nama' in request.form and 'email' in request.form and 'no_telepon' in request.form and 'foto_profile' in request.files:

        username = request.form['username']
        password = request.form['password']
        nama = request.form['nama']
        email = request.form['email']
        no_telepon = request.form['no_telepon']
        profile = request.files['foto_profile']
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM user WHERE username = %s', (username,)) # memeriksa username pada DB
        user = cursor.fetchone()
        
        if user: 
            error = 'Username sudah dipakai!' # memeriksa apakah username sudah terpakai
        elif not re.match(r'[^@]+@[^@]+\.[^@]+', email): # regex email validation
            error = 'Email yang dimasukkan salah!'
        elif not re.match(r'[A-Za-z0-9]+', username): # regex username validation
            error = 'Username harus menggunakan huruf dan angka!'
        elif not username or not password or not email or not no_telepon:
            error = 'Ada form yang belum diisi!'
        else:
            cursor.execute('INSERT INTO user VALUES (NULL, %s, %s, %s, %s, %s, %s, %s)', (username, password, nama, email, no_telepon, profile, "kurir", ))
            mysql.connection.commit()
            error = 'Account berhasil dibuat'
            return redirect(url_for('data_kurir'))


    elif request.method == 'POST':
        error = 'Ada form yang belum diisi!'
    return render_template('admin/add/add_kurir.html', error = error)






@app.route('/admin/add', methods = ['GET','POST'])
def add():
    if request.method == 'POST':
        id_barang = request.form['id_barang']
        nama_barang = request.form['nama_barang']
        harga = request.form['harga']
        deskripsi = request.form['deskripsi']
        berat = request.form['berat']
        stok = request.form['stok']
        kategori = request.form['kategori']
        image = request.files['image']

        if id_barang and nama_barang and harga and deskripsi and berat and stok and kategori and image:

            if 'image' not in request.files:
                flash('Tidak ada file','error')
            
            conn = mysql.connection
            cur = conn.cursor(MySQLdb.cursors.DictCursor)
            cur.execute("INSERT INTO barang VALUES (%s, %s, %s, %s, %s, %s, %s, %s)", (id_barang, nama_barang, harga, deskripsi, berat, stok, kategori, image, ))
            conn.commit()
            if image.filename == '':
                flash('No selected file')
            if image and format_file(image.filename):
                filename = secure_filename(image.filename)
                image.save(os.path.join(app.config["UPLOAD_FOLDER"], filename))
                print('berhasil')
                return redirect(url_for('admin'))

    return render_template('admin/add/add_item.html')





@app.route('/admin/update', methods = ['GET', 'POST'])
def update():
    nama_barang = request.form['nama_barang']
    harga = request.form['harga']
    deskripsi = request.form['deskripsi']
    berat = request.form['berat']
    stok = request.form['stok']
    kategori = request.form['kategori']
    image = request.files['image']
    id_barang = request.form['id_barang']
    data = (nama_barang, harga, deskripsi, berat, stok, kategori, image, id_barang, )
    conn = mysql.connection
    cur = conn.cursor()
    cur.execute("UPDATE barang SET nama_barang = %s, harga = %s, deskripsi = %s, berat = %s,  stok = %s, kategori = %s, image = %s WHERE id_barang = %s", data)
    conn.commit()
    flash('Data user berhasil di edit')
    return redirect(url_for('admin'))




@app.route('/delete/<int:id_barang>', methods = ['GET', 'POST'])
def delete(id_barang):
    cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cur.execute("DELETE FROM barang WHERE id_barang = %s",(id_barang,))
    mysql.connection.commit()
    flash('Barang berhasil dihapus!')
    return redirect(url_for('admin'))




if __name__ == '__main__':
    app.run(debug=True)