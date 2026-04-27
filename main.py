import os
from flask import Flask, render_template, request, url_for, redirect, session
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

app = Flask(__name__)
app.secret_key = 'mir_sladkoezhki_key'

# добавление бд
db = SQLAlchemy()

# добавление товаров напрямую в базе данных пока что
class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    description = db.Column(db.Text)
    price = db.Column(db.Integer)
    image = db.Column(db.String(200))
    category = db.Column(db.String(50))

# пользователи
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///shop.db'
db.init_app(app)

with app.app_context():
    db.create_all()


@app.route('/')
def main():
    return render_template('mainpage.html', title='Главная страница')

@app.route('/about')
def about():
    return render_template('about.html', title='О нас', active_page='about')

@app.route('/contacts', methods=['GET', 'POST'])
def contacts():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        reason = request.form['reason']
        message = request.form['message']

        # уникальное имя файла (по времени)
        filename = datetime.now().strftime("%Y-%m-%d_%H-%M-%S.txt")
        filepath = os.path.join("forms", filename)

        # содержимое файла
        content = f"""
имя заказчика: {name}
Email: {email}
Причина: {reason}
        
сообщение:
{message}"""

        # запись в файл
        with open(filepath, "w", encoding="utf-8") as file:
            file.write(content)

        return redirect(url_for('contacts'))
    return render_template('contacts.html')

@app.route('/catalog')
def catalog():
    category = request.args.get('category')

    if category:
        products = Product.query.filter_by(category=category).all()
    else:
        products = Product.query.all()

    return render_template('catalog.html', products=products)

@app.route('/cart/add/<int:product_id>', methods=['POST'])
def add_to_cart(product_id):
    cart = session.get('cart', {})
    product_id = str(product_id)

    if product_id in cart:
        cart[product_id] += 1
    else:
        cart[product_id] = 1

    session['cart'] = cart
    return redirect(url_for('catalog'))

@app.route('/cart/decrease/<int:product_id>')
def decrease_quantity(product_id):
    cart = session.get('cart', {})
    product_id = str(product_id)

    if product_id in cart:
        cart[product_id] -= 1

        if cart[product_id] <= 0:
            del cart[product_id]

    session['cart'] = cart
    return redirect(url_for('cart'))

@app.route('/cart/remove/<int:product_id>')
def remove_from_cart(product_id):
    cart = session.get('cart', {})
    product_id = str(product_id)

    if product_id in cart:
        del cart[product_id]

    session['cart'] = cart
    return redirect(url_for('cart'))

@app.route('/cart')
def cart():
    cart = session.get('cart', {})

    products = []
    total = 0

    for product_id, quantity in cart.items():
        product = Product.query.get(int(product_id))

        if product:
            item_total = product.price * quantity
            total += item_total

            products.append({
                "product": product,
                "quantity": quantity,
                "total": item_total
            })

    return render_template('cart.html', products=products, total=total)

@app.route('/login', methods=['POST'])
def login():
    user = User.query.filter_by(username=request.form['username']).first()

    if user and user.password == request.form['password']:
        session['user_id'] = user.id

    return redirect(url_for('profile'))

@app.route('/logout')
def logout():
    session.pop('user_id', None)
    return redirect(url_for('profile'))

@app.route('/change-username', methods=['POST'])
def change_username():
    user = db.session.get(User, session['user_id'])
    user.username = request.form['username']
    db.session.commit()

    return redirect(url_for('profile'))

@app.route('/change-password', methods=['POST'])
def change_password():
    user = db.session.get(User, session['user_id'])

    if user.password == request.form['old_password']:
        user.password = request.form['new_password']
        db.session.commit()

    return redirect(url_for('profile'))


@app.route('/profile')
def profile():
    user = None

    if 'user_id' in session:
        user = db.session.get(User, session['user_id'])

    return render_template('profile.html', user=user)

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        confirm = request.form['confirm_password']

        # проверка паролей
        if password != confirm:
            return "Пароли не совпадают"

        # проверка уникальности имени
        existing_user = User.query.filter_by(username=username).first()
        if existing_user:
            return "Пользователь уже существует"

        # создание пользователя
        new_user = User(
            username=username,
            password=password
        )

        db.session.add(new_user)
        db.session.commit()

        # сразу логиним
        session['user_id'] = new_user.id

        return redirect(url_for('profile'))
    return render_template('register.html')


if __name__ == '__main__':
    app.run(port=8080, host='127.0.0.1')