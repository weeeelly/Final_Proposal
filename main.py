from flask import Flask
from routes.routes import api_bp
from config.database_config import SECRET_KEY

app = Flask(__name__)
app.secret_key = SECRET_KEY

# 註冊路由藍圖
app.register_blueprint(api_bp, url_prefix='/api')

if __name__ == '__main__':
    app.run(debug=True)