from flask import Flask, request, jsonify, session, render_template, redirect, flash
import mysql.connector
import hashlib

app = Flask(__name__)
app.secret_key = "your_secret_key"

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

@app.route('/update', methods=['GET'])
def update_page():
    if 'user_id' not in session:
        flash("請先登入", "warning")
        return redirect("/")    # 正確重定向到 homepage
    return render_template("update.html")

@app.route("/signup", methods=["GET", "POST"])
def signup():
    if request.method == "POST":
        username = request.form['username']
        password = request.form['password']
        
        hashed_password = hashlib.sha256(password.encode()).hexdigest()
        
        conn = get_db_connection()
        cursor = conn.cursor()

        try:
            query = "INSERT INTO User (Username, Password) VALUES (%s, %s)"
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
            check_user_query = "SELECT Uid FROM User WHERE Username = %s"
            cursor.execute(check_user_query, (username,))
            user_exists = cursor.fetchone()

            if not user_exists:
                flash("請先註冊", "warning")
                return redirect("/")  # 返回 homepage

            # 驗證密碼
            login_query = "SELECT Uid FROM User WHERE Username = %s AND Password = %s"
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

@app.route('/search', methods=['GET'])
def search():
    if 'user_id' not in session:
        flash("請先登入", "warning")
        return redirect("/")
    return render_template("search.html")

@app.route('/get_cameras', methods=['GET'])
def get_cameras():
    if 'user_id' not in session:
        return jsonify({"error": "請先登入"}), 401

    city = request.args.get('city')
    region = request.args.get('region')

    if not city or not region:
        return jsonify({"error": "請提供縣市和區域"}), 400

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    try:
        query = """
        SELECT 
            c.Limits, 
            c.Direction, 
            c.location,
            c.Longitude,
            c.Latitude,
            p.Deptnm, 
            p.Branchnm
        FROM 
            Camera c
            JOIN Ps p ON c.location = p.location
        WHERE 
            p.City = %s AND p.Region = %s
        """
        cursor.execute(query, (city, region))
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

@app.route('/update_camera', methods=['POST'])
def update_camera():
    if 'user_id' not in session:
        return jsonify({"error": "請先登入"}), 401

    data = request.json
    location = data.get('location')
    new_limit = data.get('new_limit')

    if not location or not new_limit:
        return jsonify({"error": "請提供地址和新速限"}), 400

    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        # 更新速限
        update_query = """
        UPDATE Camera
        SET Limits = %s
        WHERE location = %s
        """
        cursor.execute(update_query, (new_limit, location))

        # 記錄更新
        log_query = """
        INSERT INTO `Update` (Uid, Address)
        VALUES (%s, %s)
        """
        cursor.execute(log_query, (session['user_id'], location))
        
        conn.commit()
        return jsonify({"message": "更新成功"})
    except Exception as e:
        conn.rollback()
        return jsonify({"error": str(e)}), 500
    finally:
        cursor.close()
        conn.close()

@app.route('/update_history', methods=['GET'])
def get_update_history():
    if 'user_id' not in session:
        return jsonify({"error": "請先登入"}), 401

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    try:
        query = """
        SELECT 
            p.City,
            p.Region,
            c.location,
            c.Limits,
            c.Direction
        FROM 
            `Update` u
            JOIN Camera c ON u.Address = c.location
            JOIN Ps p ON c.location = p.location
        WHERE 
            u.Uid = %s
        ORDER BY 
            c.location
        """
        cursor.execute(query, (session['user_id'],))
        updates = cursor.fetchall()
        return jsonify(updates)
    finally:
        cursor.close()
        conn.close()

if __name__ == '__main__':
    app.run(debug=True)
