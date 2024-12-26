from flask import Flask, request, jsonify, session, render_template, redirect, flash
import mysql.connector
from mysql.connector import pooling
import hashlib

# Flask App Initialization
app = Flask(__name__)
app.secret_key = "your_secret_key"

# Database Configuration
db_config = {
    'host': 'localhost',  # Change this to your MySQL host
    'user': 'dbuser',  # Change this to your MySQL username
    'password': '0420',  # Change this to your MySQL password
    'database': 'final'  # Change this to your MySQL database name
}

# Database Connection
def get_db_connection():
    return mysql.connector.connect(**db_config)

def query_speed_cameras(city, region):
    """
    Query speed cameras in the specified city and region.
    """
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    query = """
    SELECT 
        camera.Limits, 
        camera.Direction, 
        camera.Addr, 
        Ps.Deptnm, 
        Ps.Branchnm
    FROM 
        camera
    INNER JOIN 
        Ps ON camera.Addr = Ps.addr
    WHERE 
        Ps.CityName = %s AND Ps.RegionName = %s
    """

    cursor.execute(query, (city, region))
    results = cursor.fetchall()
    conn.close()

    return results

def update_speed_camera_limits(addr, new_limits):
    """
    Update the speed limits of the specified speed camera and record the update.
    """
    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        update_query = """
        UPDATE camera
        SET Limits = %s
        WHERE Addr = %s
        """
        cursor.execute(update_query, (new_limits, addr))

        record_query = """
        INSERT INTO update (Uid, Addr)
        VALUES (%s, %s)
        """
        cursor.execute(record_query, (session['user_id'], addr))

        conn.commit()
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        conn.close()

def validate_user(username, password):
    """
    Validate user login information.
    """
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    query = """
    SELECT Uid FROM User
    WHERE Username = %s AND Password = %s
    """
    cursor.execute(query, (username, password))
    user = cursor.fetchone()
    conn.close()

    return user

@app.route("/signup", methods=["GET", "POST"])
def signup():
    if request.method == "POST":
        username = request.form['username']
        password = request.form['password']

        # Hash the password using SHA-256
        hashed_password = hashlib.sha256(password.encode()).hexdigest()

        # Connect to the database
        conn = get_db_connection()
        cursor = conn.cursor()

        try:
            # Use a parameterized query to insert the user
            query = "INSERT INTO users (username, password) VALUES (%s, %s)"
            cursor.execute(query, (username, hashed_password))
            conn.commit()
            flash("Account created successfully! Please log in.", "success")
            return redirect("/")
        except mysql.connector.IntegrityError:
            flash("Username already exists. Please choose another one.", "danger")
        finally:
            cursor.close()
            conn.close()
    
    return render_template("signup.html")
@app.route("/", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form['username']
        password = request.form['password']

        # Hash the input password using SHA-256
        hashed_password = hashlib.sha256(password.encode()).hexdigest()

        # Connect to the database
        conn = get_db_connection()
        cursor = conn.cursor()

        # Use a parameterized query to prevent SQL injection
        query = "SELECT password FROM users WHERE username = %s"
        cursor.execute(query, (username,))
        result = cursor.fetchone()

        if result and result[0] == hashed_password:
            # Credentials are correct
            session['username'] = username
            return redirect("/welcome")
        else:
            # Invalid credentials
            flash("Invalid username or password.", "danger")

        # Close the connection
        cursor.close()
        conn.close()
    
    return render_template("login.html")

# Welcome Page
@app.route("/welcome")
def welcome():
    if 'username' not in session:
        return redirect("/")
    return render_template("welcome.html")


@app.route("/logout")
def logout():
    session.pop('username', None)
    return redirect("/")


@app.route('/query_speed_cameras', methods=['GET'])
def get_speed_cameras():
    """
    Query speed cameras based on city and region.
    """
    if 'user_id' not in session:
        flash("Please log in first.", "warning")
        return redirect("/")

    city = request.args.get('city')
    region = request.args.get('region')

    if not city or not region:
        return jsonify({"error": "Please provide both city and region."}), 400

    try:
        data = query_speed_cameras(city, region)
        return jsonify(data)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/update_speed_camera', methods=['POST'])
def update_speed_camera():
    """
    Update the speed limits of a specific speed camera.
    """
    if 'user_id' not in session:
        flash("Please log in first.", "warning")
        return redirect("/")

    data = request.get_json()
    addr = data.get('addr')
    new_limits = data.get('new_limits')

    if not addr or not new_limits:
        return jsonify({"error": "Please provide both addr and new_limits."}), 400

    try:
        update_speed_camera_limits(addr, new_limits)
        return jsonify({"message": "Speed camera limits updated successfully."})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/update_history', methods=['GET'])
def update_history():
    """
    View user update history.
    """
    if 'user_id' not in session:
        flash("Please log in first.", "warning")
        return redirect("/")

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    try:
        query = """
        SELECT p.City,
            p.Region,
            c.location,
            c.Limits,
            c.Direction 
        FROM 
            `Update` u
            JOIN Camera c ON u.Address = c.location
            JOIN Ps p ON c.location = p.location 
        WHERE Uid = %s
        ORDER BY 
            c.location
        """
        cursor.execute(query, (session['user_id'],))
        updates = cursor.fetchall()
        return jsonify(updates)
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        conn.close()

if __name__ == '__main__':
    app.run(debug=True)
