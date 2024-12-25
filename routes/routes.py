from flask import Blueprint, request, jsonify, session
from models.user_model import UserModel
from models.camera_model import CameraModel

# 創建藍圖
api_bp = Blueprint('api', __name__)

def login_required(f):
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return jsonify({"error": "請先登入"}), 401
        return f(*args, **kwargs)
    return decorated_function

@api_bp.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    username = data.get('username', '').strip()
    password = data.get('password', '').strip()

    if not username or not password:
        return jsonify({"error": "使用者名稱和密碼不能為空"}), 400

    try:
        UserModel.register_user(username, password)
        return jsonify({"message": "註冊成功"}), 201
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        return jsonify({"error": "註冊失敗"}), 500

@api_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    username = data.get('username', '').strip()
    password = data.get('password', '').strip()

    if not username or not password:
        return jsonify({"error": "使用者名稱和密碼不能為空"}), 400

    try:
        user = UserModel.validate_user(username, password)
        if user:
            session['user_id'] = user['Uid']
            return jsonify({"message": "登入成功"}), 200
        return jsonify({"error": "使用者名稱或密碼錯誤"}), 401
    except Exception as e:
        return jsonify({"error": "登入失敗"}), 500

@api_bp.route('/logout', methods=['POST'])
def logout():
    session.pop('user_id', None)
    return jsonify({"message": "登出成功"}), 200

@api_bp.route('/cameras', methods=['GET'])
@login_required
def get_cameras():
    city = request.args.get('city', '').strip()
    region = request.args.get('region', '').strip()
    
    if not city or not region:
        return jsonify({"error": "請提供城市和地區"}), 400

    try:
        cameras = CameraModel.get_cameras(city, region)
        return jsonify(cameras), 200
    except Exception as e:
        return jsonify({"error": "查詢失敗"}), 500

@api_bp.route('/cameras/update', methods=['POST'])
@login_required
def update_camera():
    data = request.get_json()
    address = data.get('address', '').strip()
    new_limit = data.get('new_limit')

    if not address or not new_limit:
        return jsonify({"error": "請提供地址和新速限"}), 400

    try:
        CameraModel.update_camera(address, new_limit, session['user_id'])
        return jsonify({"message": "更新成功"}), 200
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        return jsonify({"error": "更新失敗"}), 500

@api_bp.route('/cameras/history', methods=['GET'])
@login_required
def get_history():
    try:
        history = CameraModel.get_update_history(session['user_id'])
        return jsonify(history), 200
    except Exception as e:
        return jsonify({"error": "查詢歷史記錄失敗"}), 500