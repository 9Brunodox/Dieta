from database import db

class Meal(db.Model):
    __tablename__ = 'meals'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    nome = db.Column(db.String(100), nullable=False)
    descricao = db.Column(db.String(200), nullable=False)
    calorias = db.Column(db.Integer, nullable=False)
    na_dieta = db.Column(db.Boolean, nullable=False)
    registro = db.Column(db.DateTime, nullable=False)

    user = db.relationship('User', back_populates="meal")
    
    