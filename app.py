from flask import Flask, request, jsonify
from database import db
from flask_login import LoginManager, login_user, logout_user, current_user, login_required # Responsável por fazer o gerenciamento de sessões de usuários
from models.user import User
from models.meal import Meal

app = Flask(__name__)
app.config['SECRET_KEY'] = "KEY"
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'

login_manager = LoginManager()

db.init_app(app)
login_manager.init_app(app)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@app.route('/login', methods=['POST'])
def login():
    data = request.json
    username = data.get('username')
    password = data.get('password')

    if username and password:
        user = User.query.filter_by(username=username).first()
        if user and user.password == password:
            login_user(user)
            return jsonify({"message": "Login bem-sucedido!"}), 200
    return jsonify({"message": "Credenciais inválidas!"}), 400

@app.route('/logout', methods=['GET'])
@login_required
def logout():
    logout_user()
    return jsonify({"message": "Logout bem-sucedido!"}), 200

@app.route('/create_user', methods=['POST'])
def create_user():
    data = request.json
    username = data.get('username')
    password = data.get('password')
    if username and password:
        if User.query.filter(username="username").first():
            return jsonify({"message": "Usuário já existe!"}), 400
        new_user = User(username=username, password=password)
        db.session.add(new_user)
        db.session.commit()
        return jsonify({"message": "Usuário criado com sucesso!"}), 201
    return jsonify({"message": "Dados do usuário inválidos!"}), 400

@app.route('/user/delete/<int:user_id>', methods=['DELETE'])
@login_required
def delete_user(user_id):
    user = User.query.get(user_id)
    if user:
        db.session.delete(user)
        db.session.commit()
        return jsonify({"message": "Usuário deletado com sucesso!"}), 200
    return jsonify({"message": "Usuário não encontrado!"}), 404

@app.route('/meal/create', methods=['POST'])
@login_required
def create_meal():
    data = request.json
    meal_name = data.get('nome')
    meal_description = data.get('description')
    meal_calories = data.get('calorias')

    if meal_name and meal_description and meal_calories:
        if isinstance(meal_calories, int) and meal_calories >= 0:
            if meal_calories <= 600:
                na_dieta = True
            else:
                na_dieta = False
        else:
            return jsonify({"message": "Calorias devem ser um número inteiro não negativo!"}), 400
    meal = Meal(
        name = meal_name,
        descricao=meal_description,
        calorias=meal_calories,
        na_dieta=na_dieta,
        user_id=current_user.id
    )
    db.session.add(meal)
    db.session.commit()
    return jsonify({"message": "Dados da refeição inválidos!"}), 400



if __name__ == '__main__':
    app.run(debug=True)