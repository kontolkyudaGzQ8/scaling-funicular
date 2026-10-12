from flask import Flask, flash, jsonify, redirect, request, session, url_for
from werkzeug.utils import secure_filename

import os

from controller import Controller

def register_routes(app: Flask): 
    controller = Controller(session)

    @app.context_processor
    def inject_keranjang():
        jumlah = 0
        if 'keranjang' in session:
            jumlah = len(session["keranjang"])

        return dict(jumlah_keranjang=jumlah, session=session)   

    @app.before_request
    def before_req(): 
        path = request.path
        
        if session and session["type"] == "admin": 
            not_allowed_paths = ["/", "/login", "/superadmin-login", "/admin"]
            for not_allowed_path in not_allowed_paths: 
                if not_allowed_path.startswith(path): 
                    return redirect(url_for("dashboard"))
                
        elif session and session["type"] == "superadmin": 
            not_allowed_paths = ["/", "/login", "/superadmin-login"]
            for not_allowed_path in not_allowed_paths: 
                if not_allowed_path.startswith(path): 
                    print(path)
                    return redirect(url_for("dashboard"))
        else:   
            allowed_paths = ["/", "/login", "/superadmin-login", "/static", "/"]
            if path not in allowed_paths:
                return redirect(url_for("index"))
    
    @app.route("/")
    def index(): 
        return redirect(url_for("login")), 302
    
    @app.route("/dashboard")
    def dashboard(): 
        produk_list, err = controller.produk.get_produk()
        penjualan_by_produk = controller.penjualan.get_penjualan_group_by_produk()
        penjualan_list = controller.penjualan.get_penjualan_normalize()
        total_produk_tersedia = controller.produk.get_produk_stok_available_count()
        total_produk_kosong = controller.produk.get_produk_stok_empty_count()

        return controller.dashboard.show_dashboard_view(
            produk_list=produk_list,
            penjualan_by_produk=penjualan_by_produk,
            penjualan_list=penjualan_list,
            total_produk_tersedia=total_produk_tersedia,
            total_produk_kosong=total_produk_kosong
        ), 200
        
    @app.route("/login", methods=["GET", "POST"])
    def login(): 
        if request.method == "GET": 
            return controller.admin.show_login_view()
        
        username = request.form.get("username", "")
        password = request.form.get("password", "")

        admin, err = controller.admin.get_admin(username, password)
        if err: 
            return controller.admin.show_login_view(error=err)
                
        session["username"] = username
        session["password"] = password
        session["nama"] = admin.nama
        session["shift"] = admin.shift.value
        session["shift_time"] = "06:00 - 15:00" if admin.shift.value == "pagi" else "14:00 - 22:00"
        session["type"] = "admin"
        
        return redirect(url_for("dashboard")), 302
    
    @app.route("/superadmin-login", methods=["GET", "POST"])
    def superadmin_login(): 
        if request.method == "GET": 
            return controller.super_admin.show_login_view()
        
        username = request.form.get("username", "")
        password = request.form.get("password", "")

        super_admin, err = controller.super_admin.get_superadmin(username, password)
        if err: 
            return controller.super_admin.show_login_view(error=err)
                
        session["username"] = username
        session["password"] = password
        session["nama"] = super_admin.nama
        session["type"] = "superadmin"
        
        return redirect(url_for("dashboard")), 302
    
    @app.route("/logout")
    def logout(): 
        login_page = "login" if session["type"] == "admin" else "superadmin_login"
        session.clear()
        return redirect(url_for(login_page)), 302
    
    @app.route("/admin")
    def admin(): 
        admin_list, err = controller.admin.get_admin()
        return controller.dashboard.show_admin_view(admin_list=admin_list), 200
    
    @app.route("/admin/tambah", methods=["POST"])
    def tambah_admin(): 
        username = request.form.get("username", "")
        password = request.form.get("password", "")
        name = request.form.get("nama", "")
        shift = request.form.get("shift", "")

        msg, err = controller.admin.insert_admin(username, password, name, shift)
        if err: 
            flash(err, "error")
            return redirect(url_for("admin")), 302
        
        flash(msg, "success")
        return redirect(url_for("admin")), 302
    
    @app.route("/admin/edit/<string:username>", methods=["POST"])
    def edit_admin(username: str): 
        password = request.form.get("password", "")
        name = request.form.get("nama", "")
        shift = request.form.get("shift", "")

        msg, err = controller.admin.update_admin(username, password, name, shift)
        if err: 
            flash(err, "error")
            return redirect(url_for("admin")), 302
        
        flash(msg, "success")
        return redirect(url_for("admin")), 302
    
    @app.route("/admin/hapus/<string:username>", methods=["POST"])
    def hapus_admin(username: str): 
        msg, err = controller.admin.delete_admin(username)
        if err: 
            flash(err, "error")
            return redirect(url_for("admin")), 302
        
        flash(msg, "success")
        return redirect(url_for("admin")), 302

    @app.route("/produk")
    def produk(): 
        produk_list, err = controller.produk.get_produk()
        if err and produk_list == None: 
            return err, 401
        
        return controller.produk.show_produk_view(produk_list=produk_list), 200
    
    @app.route("/produk/tambah", methods=["POST"])
    def tambah_produk(): 
        nama = request.form.get("nama", "")
        jumlah = request.form.get("jumlah", "")
        harga = request.form.get("harga", "")
        kategori = request.form.get("kategori", "")

        # Ambil file gambar
        file = request.files.get("gambar")
        gambar_filename = ""

        if file and file.filename != "":
            filename = secure_filename(file.filename)
            gambar_filename = filename     
            file.save(os.path.join(app.config["UPLOAD_FOLDER"], gambar_filename))

        msg, err = controller.produk.insert_produk(nama, jumlah, harga, kategori, gambar_filename)
        if err: 
            flash(err, "error")
            return redirect(url_for("produk")), 302
        
        flash(msg, "success")
        return redirect(url_for("produk")), 302
    
    @app.route("/produk/edit/<string:id>", methods=["GET", "POST"])
    def edit_produk(id: str): 
        if request.method == "GET": 
            produk, err = controller.produk.get_produk(id=id)
            if err: 
                return err, 401
            
            return controller.produk.show_edit_produk_view(produk=produk), 200
        
        nama = request.form.get("nama", "")
        jumlah = request.form.get("jumlah", "")
        harga = request.form.get("harga", "")
        kategori = request.form.get("kategori", "")

        # Ambil file gambar
        file = request.files.get("gambar")
        gambar_filename = ""

        if file and file.filename != "":
            filename = secure_filename(file.filename)
            gambar_filename = filename     
            file.save(os.path.join(app.config["UPLOAD_FOLDER"], gambar_filename))

        msg, err = controller.produk.edit_produk(id, nama, jumlah, harga, kategori, gambar_filename)
        if err: 
            flash(err, "error")
            return redirect(url_for("produk")), 302
        
        flash(msg, "success")
        return redirect(url_for("produk")), 302

    @app.route("/produk/hapus/<string:id>", methods=["POST"])
    def hapus_produk(id: str): 
        msg, err = controller.produk.delete_produk(id)
        if err: 
            flash(err, "error")
            return redirect(url_for("produk")), 302
        
        flash(msg, "success")  # Menampilkan notifikasi di halaman berikutnya
        return redirect(url_for("produk")), 302

    @app.route("/penjualan")
    def penjualan(): 
        produk_list, err = controller.produk.get_produk() 
        if err: 
            return err, 401
        
        penjualan_list, err = controller.penjualan.get_penjualan()
        if err and penjualan_list == None: 
            return err, 401

        return controller.penjualan.show_penjualan_view(produk_list=produk_list, penjualan_list=penjualan_list)
    

    @app.route("/penjualan/edit/<string:id>", methods=["POST"])
    def edit_penjualan(id: str):         
        id = request.form.get("id", "") 
        produk_id = request.form.get("produk_id", "")
        jumlah = request.form.get("jumlah", "")
        tanggal = request.form.get("tanggal", "")

        msg, err = controller.penjualan.edit_penjualan(id=id, produk_id=produk_id, jumlah=jumlah, tanggal=tanggal)
        if err: 
            flash(err, "error")
            return redirect(url_for("penjualan")), 302
        
        flash(msg, "success")
        return redirect(url_for("penjualan")), 302

    @app.route("/penjualan/hapus/<string:id>", methods=["POST"])
    def hapus_penjualan(id: str): 
        msg, err = controller.penjualan.delete_penjualan(id=id)
        if err: 
            flash(err, "error")
            return redirect(url_for("penjualan")), 302

        flash(msg, "success")  # Menampilkan notifikasi di halaman berikutnya
        return redirect(url_for("penjualan")), 302
    
    @app.route("/keranjang")
    def keranjang(): 
        keranjang_list, err = controller.keranjang.get_keranjang(session)
        if err: 
            return err, 401
        
        return controller.keranjang.show_keranjang_view(keranjang_list=keranjang_list) 
    
    @app.route("/keranjang/tambah/<string:id>", methods=["POST"])
    def tambah_keranjang(id: str): 
        if request.method == "POST": 
            produk_id = id
            jumlah = request.form.get("jumlah", "")

            msg, err = controller.keranjang.insert_keranjang(produk_id, jumlah, session)
            if err: 
                flash(err, "error")
                return redirect(url_for("pembelian"))
            
            flash(msg, "success")
            return redirect(url_for("pembelian"))
    
    @app.route("/keranjang/edit/<string:id>", methods=["POST"])
    def edit_keranjang(id: str): 
        if request.method == "POST": 
            jumlah = request.form.get("jumlah", "")
            msg, err = controller.keranjang.edit_keranjang(id, jumlah, session)
            if err: 
                return jsonify({"error": err}), 200
            
            return jsonify({"message": msg}), 200
    
    @app.route("/keranjang/hapus/<string:id>", methods=["POST"])
    def hapus_keranjang(id: str): 
        msg, err = controller.keranjang.delete_keranjang(session, id)
        if err: 
            flash(err, "error")
            return redirect(url_for("keranjang")), 302
        
        flash(msg, "success")  # Menampilkan notifikasi di halaman berikutnya
        return redirect(url_for("keranjang")), 302
    
    @app.route("/pembelian")
    def pembelian(): 
        produk_list, err = controller.produk.get_produk() 
        if err: 
            return err, 401
        return controller.pembelian.show_pembelian_view(produk_list=produk_list)
    
    @app.route("/pembayaran", methods=["POST"])
    def pembayaran(): 
        keranjang, err = controller.keranjang.get_keranjang(session)
        if err: 
            return jsonify({"error": err}), 200
        
        msg, err = controller.penjualan.insert_penjualan(keranjang)
        if err: 
            return jsonify({"error": err}), 200
        
        return jsonify({"message": msg}), 200
    
    @app.route("/pengaturan")
    def pengaturan(): 
        return controller.pengaturan.show_pengaturan_view(session=session)
    
    @app.route("/apriori", methods=["GET", "POST"])
    def apriori(): 
        if request.method == "GET": 
            return controller.apriori.show_apriori_view(), 200
        
        min_support = request.form.get("min_support", "") 
        min_confidence = request.form.get("min_confidence", "")

        frequent_itemsets, level_rules, err = controller.apriori.hitung(min_sup=min_support, min_conf=min_confidence)
        if err: 
            flash(err, "error")
            return redirect(url_for("apriori")), 302
        
        return controller.apriori.show_apriori_view(level_rules=level_rules, frequent_itemsets=frequent_itemsets), 200

               
    return app

    