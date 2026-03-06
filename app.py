from flask import Flask
from models import db, User


from routes.auth_routes import auth_bp
from routes.admin_routes import admin_bp
from routes.company_routes import company_bp
from routes.student_routes import student_bp

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///placement.db'
app.config['SECRET_KEY'] = 'supersecretkey'


db.init_app(app)


app.register_blueprint(auth_bp)
app.register_blueprint(admin_bp)
app.register_blueprint(company_bp)
app.register_blueprint(student_bp)

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        
        
        if not User.query.filter_by(role='admin').first():
           
            admin = User(email='admin@portal.com', password='admin123', role='admin')
            db.session.add(admin)
            db.session.commit()
            print("Admin created: admin@portal.com / admin123")
            
    app.run(debug=True)