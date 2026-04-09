from flask import Flask, render_template

app = Flask(__name__)


@app.route('/')
def main():
    return render_template('mainpage.html', title='Главная страница')

@app.route('/about')
def about():
    return render_template('about.html', title='О нас', active_page='about')

@app.route('/contacts')
def contacts():
    return render_template('contacts.html', title='Каталог', active_page='contacts')

@app.route('/catalog')
def catalog():
    return

@app.route('/cart')
def cart():
    return

@app.route('/profile')
def profile():
    return


if __name__ == '__main__':
    app.run(port=8080, host='127.0.0.1')