from flask import Flask, render_template, request, redirect, url_for, session
from flask_sqlalchemy import SQLAlchemy
import os

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # تغييره إلى مفتاح أمان قوي عند الاستخدام الفعلي
# تحديد المسار النسبي لملف قاعدة البيانات خارج المجلد التطبيق
db_path = os.path.join(os.path.dirname(__file__), 'users.db')
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + db_path
db = SQLAlchemy(app)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(80), nullable=False)

@app.route('/')
def index():
    return render_template('login.html')

@app.route('/login', methods=['POST'])
def login():
    username = request.form['username']
    password = request.form['password']

    user = User.query.filter_by(username=username, password=password).first()

    if user:
        session['username'] = username  # حفظ اسم المستخدم في الجلسة
        return redirect(url_for('facebook_page'))
    else:
        return 'فشل تسجيل الدخول'

@app.route('/register', methods=['POST'])
def register_user():
    username = request.form['username']
    password = request.form['password']

    # التحقق من وجود المستخدم قبل إضافته
    existing_user = User.query.filter_by(username=username).first()

    if existing_user:
        return 'اسم المستخدم موجود بالفعل!'
    
    # إضافة المستخدم إذا كان غير موجود
    new_user = User(username=username, password=password)
    db.session.add(new_user)
    db.session.commit()

    session['username'] = username  # حفظ اسم المستخدم في الجلسة
    return redirect(url_for('facebook_page'))

@app.route('/facebook')
def facebook_page():
    if 'username' in session:
        return 'مرحبًا {} في صفحة فيسبوك!'.format(session['username'])
    else:
        return redirect(url_for('index'))

@app.route('/change_password', methods=['GET', 'POST'])
def change_password():
    if request.method == 'POST':
        old_password = request.form['old_password']
        new_password = request.form['new_password']
        confirmed_password = request.form['confirmed_password']

        # تحقق من صحة كلمة المرور القديمة
        username = session.get('username', None)
        user = User.query.filter_by(username=username, password=old_password).first()

        if user and new_password == confirmed_password:
            # قم بتحديث كلمة المرور
            user.password = new_password
            db.session.commit()
            return 'تم تغيير كلمة المرور بنجاح!'
        else:
            return 'فشل تغيير كلمة المرور، يرجى التحقق من البيانات المدخلة.'

    return render_template('change_password.html')

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
