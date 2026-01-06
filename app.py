from flask import Flask, request, jsonify
from database import db
from flask_login import LoginManager

app = Flask(__name__)
app.config['SECRET_KEY'] = "KEY"
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'

login_manager = LoginManager()
db.init_app(app)
login_manager.init_app(app)

@app.route('/login', methods=['POST'])
def login():
    data = request.json
    username = data.get('username')
    password = data.get('password')

    if username and password:
        pass
    return jsonify({"message": "Credenciais inválidas!"}), 400



@app.route('/register', methods=['POST'])
def register():
    ...

if __name__ == '__main__':
    app.run(debug=True)