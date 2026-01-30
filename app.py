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
        if User.query.filter_by(username=username).first():
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

@app.route('/user/update/<int:user_id>', methods=['PATCH'])
@login_required
def update_user(user_id):
    user = User.query.get(user_id)
    if not user:
        return jsonify({"message": "Usuário não encontrado!"}), 404
    data = request.json
    username = data.get("username")
    password = data.get("password")
    if username:
        user.username = username
    if password:
        user.password = password
    db.session.commit()
    return jsonify({"message": "Usuário atualizado com sucesso!"}), 200


@app.route('/meal/create', methods=['POST'])
@login_required
def create_meal():
    data = request.json
    meal_name = data.get('meal_name')
    meal_description = data.get('meal_description')
    meal_calories = data.get('meal_calories')

    if meal_name is None or meal_description is None or meal_calories is None:
        return jsonify({"message": "Calorias devem ser um número inteiro não negativo!"}), 400
    
    if not isinstance(meal_calories, int) or meal_calories < 0:
        return jsonify({"message": "Calorias devem ser um número inteiro não negativo!"}), 400
    
    na_dieta = meal_calories <= 600

    meal = Meal(
        nome = meal_name,
        descricao=meal_description,
        calorias=meal_calories,
        na_dieta=na_dieta,
        user_id=current_user.id,
        registro=db.func.current_timestamp()
    )
    db.session.add(meal)
    db.session.commit()
    return jsonify({"message": "Refeição criada com sucesso!"}), 201

@app.route('/meal/delete/<int:meal_id>', methods=['DELETE'])
@login_required
def delete_meal():
    data = request.json
    meal_id = data.get('id')
    if meal_id:
        meal = Meal.query.get(meal_id)
        if meal and meal.user_id == current_user.id:
            db.session.delete(meal)
            db.session.commit()
            return jsonify({"message": "Refeição deletada com sucesso!"}), 200
    return jsonify({"message": "Refeição não encontrada!"}), 404

@app.route('/meals', methods=['GET'])
@login_required
def get_meals():
    meals = Meal.query.filter_by(user_id=current_user.id).all()
    
    meals_list = [{
        "id": meal.id,
        "name": meal.nome,
        "description": meal.descricao,
        "calories": meal.calorias,
        "na_dieta": meal.na_dieta
    } for meal in meals]

    return jsonify({"total": len(meals_list), "items": meals_list}), 200


@app.route('/meal/<int:meal_id>', methods=['GET'])
@login_required
def get_meal(meal_id):
    meal = Meal.query.filter_by(id=meal_id, user_id=current_user.id).first()
    if not meal:
        return jsonify({"message": "Refeição não encontrada!"}), 404
    meal_data = {
        "id": meal.id,
        "name": meal.nome,
        "description": meal.descricao,
        "calories": meal.calorias,
        "na_dieta": meal.na_dieta
    }
    return jsonify(meal_data), 200

@app.route('/meal/<int:meal_id>', methods=['PATCH'])
@login_required
def update_meal(meal_id):
    meal = Meal.query.filter_by(id=meal_id, user_id=current_user.id).first()
    if not meal:
        return jsonify({"message": "Refeição não encontrada!"}), 404
    data = request.json
    meal_name = data.get('meal_name')
    meal_description = data.get('meal_description')
    meal_calories = data.get('meal_calories')

    if meal_name:
        meal.nome = meal_name
    if meal_description:
        meal.descricao = meal_description
    if meal_calories:
        meal.calorias = meal_calories
        meal.na_dieta = meal_calories <= 600
    db.session.commit()
    return jsonify({"message": "Refeição atualizada com sucesso!"}), 200

if __name__ == '__main__':
    app.run(debug=True)