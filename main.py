from flask import Flask, render_template, request, url_for, redirect, session
from flask_sqlalchemy import SQLAlchemy

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

@app.route('/contacts')
def contacts():
    return render_template('contacts.html', title='Контакты', active_page='contacts')

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

@app.route('/profile')
def profile():
    return render_template('profile.html', title='Профиль', active_page='profile')


if __name__ == '__main__':
    app.run(port=8080, host='127.0.0.1')