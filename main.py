from flask import Flask, request, jsonify, session, render_template, redirect, flash
import mysql.connector
import hashlib
import os

app = Flask(__name__)
app.secret_key = os.urandom(24)

# Database Configuration
db_config = {
    'host': 'localhost',
    'user': 'dbuser',
    'password': '0420',
    'database': 'final'
}

def get_db_connection():
    return mysql.connector.connect(**db_config)

@app.route("/")
def home():
    return render_template("home.html")

@app.route('/search', methods=['GET'])
def search():
    if 'user_id' not in session:
        flash("請先登入", "warning")
        return redirect("/")    # 正確重定向到 homepage
    return render_template("search.html")


@app.route("/signup", methods=["GET", "POST"])
def signup():
    if request.method == "POST":
        username = request.form['username']
        password = request.form['password']
        
        hashed_password = hashlib.sha256(password.encode()).hexdigest()
        
        conn = get_db_connection()
        cursor = conn.cursor()

        try:
            query = "INSERT INTO users (username, password) VALUES (%s, %s)"
            cursor.execute(query, (username, hashed_password))
            conn.commit()
            flash("註冊成功！", "success")
            return redirect("/")  # 註冊成功返回 homepage
        except mysql.connector.IntegrityError:
            flash("用戶名已存在，請選擇其他用戶名", "danger")
            return render_template("signup.html")  # 保持在註冊頁面
        finally:
            cursor.close()
            conn.close()
    
    return render_template("signup.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form['username']
        password = request.form['password']
        
        hashed_password = hashlib.sha256(password.encode()).hexdigest()
        
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        try:
            # 先檢查用戶是否存在
            check_user_query = "SELECT Uid FROM users WHERE username = %s"
            cursor.execute(check_user_query, (username,))
            user_exists = cursor.fetchone()

            if not user_exists:
                flash("請先註冊", "warning")
                return redirect("/")  # 返回 homepage

            # 驗證密碼
            login_query = "SELECT Uid FROM users WHERE username = %s AND Password = %s"
            cursor.execute(login_query, (username, hashed_password))
            user = cursor.fetchone()

            if user:
                session['user_id'] = user['Uid']
                flash("登入成功！", "success")
                return redirect("/")  # 登入成功返回 homepage
            else:
                flash("密碼錯誤", "danger")
                return render_template("login.html")
        finally:
            cursor.close()
            conn.close()
    
    return render_template("login.html")

@app.route("/logout")
def logout():
    session.pop('user_id', None)
    flash("已登出", "success")
    return redirect("/")



@app.route('/get_cameras', methods=['GET'])
def get_cameras():
    if 'user_id' not in session:
        return jsonify({"error": "請先登入"}), 401

    city = request.args.get('CityName')
    region = request.args.get('RegionName')

    if not city:
        return jsonify({"error":"請選擇縣市(區域)"}), 400

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    try:
        if city and region:
            query = """
            SELECT 
                c.Limits, 
                c.Direct, 
                c.Addr,
                p.DeptNm, 
                p.BranchNm
            FROM 
                camera c
                JOIN ps p ON c.Addr = p.Addr
            WHERE 
                p.CityName = %s AND p.RegionName = %s
            ORDER BY
                c.Addr desc
            """
            cursor.execute(query, (city, region))
            results = cursor.fetchall()
            return jsonify(results)
        else:
            query = """
            SELECT 
                c.Limits, 
                c.Direct, 
                c.Addr,
                p.DeptNm, 
                p.BranchNm
            FROM 
                camera c
                JOIN ps p ON c.Addr = p.Addr
            WHERE 
                p.CityName = %s
            ORDER BY
                c.Addr desc
            """
            cursor.execute(query, (city,))
            results = cursor.fetchall()
            return jsonify(results)
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        cursor.close()
        conn.close()

@app.route('/update', methods=['GET'])
def update_page():
    if 'user_id' not in session:
        flash("請先登入", "warning")
        return redirect("/")
    return render_template("update.html")

@app.route('/add_camera', methods=['POST'])
def add_camera():
    data = request.json
    city = data.get('CityName')
    region = data.get('RegionName')
    addr = data.get('Addr')
    limits = data.get('Limits')
    direction = data.get('Direct')

    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        insert_query_camera = """
        INSERT INTO camera (Addr, Direct, Limits)
        VALUES (%s, %s, %s)
        """
        insert_query_ps = """
        INSERT INTO ps (CityName, RegionName, Addr, DeptNm, BranchNm)
        VALUES (%s, %s, %s, %s, %s)
        """
        cursor.execute(insert_query_camera, (addr, direction, limits))
        cursor.execute(insert_query_ps, (city, region, addr, '他人新增', '他人新增'))

        log_query = """
        INSERT INTO records (Uid, CityName, RegionName, Addr, Direct, Limits)
        VALUES (%s, %s, %s, %s, %s, %s)
        """
        cursor.execute(log_query, (session['user_id'], city, region, addr, direction, limits))
        
        conn.commit()
        flash("新增成功！", "success")
    except Exception as e:
        conn.rollback()
        flash(f"新增失敗: {str(e)}", "danger")
    finally:
        cursor.close()
        conn.close()

    return redirect("/update")

@app.route('/delete_camera', methods=['POST'])
def delete_camera():
    data = request.json
    city = data.get('CityName')
    region = data.get('RegionName')
    addr = data.get('Addr')
    direction = data.get('Direct')
    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        # 執行刪除操作
        delete_query = """
        DELETE FROM camera
        WHERE Addr = %s AND Direct = %s
        """
        cursor.execute(delete_query, (addr, direction))
        if cursor.rowcount == 0:  # 確認是否有刪除成功
            flash("刪除失敗：找不到指定地址", "danger")
        else:
            # 記錄刪除操作
            log_query = """
            INSERT INTO records (Uid, CityName, RegionName, Addr, Direct)
            VALUES (%s, %s, %s, %s, %s)
            """
            cursor.execute(log_query, (session['user_id'], city, region, addr, direction))
            conn.commit()
            flash("刪除成功", "success")
    except Exception as e:
        conn.rollback()
        flash(f"刪除失敗：{str(e)}", "danger")
    finally:
        cursor.close()
        conn.close()

    return redirect("/update")

@app.route('/update_camera', methods=['POST'])
def update_camera():
    if 'user_id' not in session:
        flash("請先登入", "warning")
        return redirect("/update")

    data = request.json
    addr = data.get('Addr')
    city = data.get('CityName')
    region = data.get('RegionName')
    direct = data.get('Direct')
    new_limit = data.get('new_limit')

    if not addr or not new_limit:
        flash("請提供地址和新速限", "danger")
        return redirect("/update")

    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        update_query = """
        UPDATE camera
        SET Limits = %s
        WHERE Addr = %s
        """
        cursor.execute(update_query, (new_limit, addr))

        log_query = """
        INSERT INTO records (Uid, CityName, RegionName, Addr, Direct, Limits)
        VALUES (%s, %s, %s, %s, %s, %s)
        """
        cursor.execute(log_query, (session['user_id'], city, region, addr, direct, new_limit))
        
        conn.commit()
        flash("更新成功", "success")
        return redirect("/update")
    except Exception as e:
        conn.rollback()
        flash(f"更新失敗: {str(e)}", "danger")
        return redirect("/update")
    finally:
        cursor.close()
        conn.close()


@app.route('/history')
def history():
    if 'user_id' not in session:
        flash("請先登入", "warning")
        return redirect("/")
    return render_template("history.html")

@app.route('/get_update_history', methods=['GET'])
def get_update_history():
    if 'user_id' not in session:
        return jsonify({"error": "請先登入"}), 401

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    try:
        query = """
        SELECT 
            uh.CityName,
            uh.RegionName, 
            uh.Addr,
            uh.Direct,
            u.username,
            uh.Limits
        FROM 
            records uh
            JOIN users u ON uh.Uid = u.Uid
        WHERE 
            uh.Uid = %s
       
        """
        cursor.execute(query, (session['user_id'],))
        updates = cursor.fetchall()
        return jsonify(updates)
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        cursor.close()
        conn.close()
if __name__ == '__main__':
    app.run(debug=True)
