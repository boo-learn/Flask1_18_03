import os
from flask import Flask, jsonify, abort, request, g
from pathlib import Path
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

# Документация по миграциям: https://flask-migrate.readthedocs.io/en/latest/

BASE_DIR = Path(__file__).parent

app = Flask(__name__)
app.config['JSON_AS_ASCII'] = False

if os.environ.get('DATABASE_URL'):
    path_to_db = os.environ.get('DATABASE_URL').replace("://", "ql://", 1)
else:
    path_to_db = f"sqlite:///{BASE_DIR / 'main.db'}"
app.config['SQLALCHEMY_DATABASE_URI'] = path_to_db

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
migrate = Migrate(app, db)


class AuthorModel(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(32), unique=True)
    surname = db.Column(db.String(32), nullable=False, server_default="Иванов")
    quotes = db.relationship('QuoteModel', backref='author', lazy='dynamic')

    def __init__(self, name, surname="Иванов"):
        self.name = name
        self.surname = surname

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "surname": self.surname
        }


class QuoteModel(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    author_id = db.Column(db.Integer, db.ForeignKey(AuthorModel.id))
    text = db.Column(db.String(255), unique=False)

    def __init__(self, author, text):
        self.author_id = author.id
        self.text = text

    def to_dict(self):
        return {
            "id": self.id,
            "author": self.author.to_dict(),
            "text": self.text
        }


# AUTHORS
@app.route("/authors", methods=["POST"])
def create_author():
    author_data = request.json
    author = AuthorModel(**author_data)
    db.session.add(author)
    db.session.commit()
    return author.to_dict(), 201


# QUOTES
#                      .to_dict()        jsonify()
# Сериализация: object ----------> dict ----------> json
@app.route("/quotes")
def quotes_list():
    # authors = AuthorModel.query.all()
    quotes = QuoteModel.query.all()
    quotes = [quote.to_dict() for quote in quotes]
    return jsonify(quotes), 200


@app.route("/quotes/<int:quote_id>")
def get_quote_by_id(quote_id):
    quote = QuoteModel.query.get(quote_id)
    if quote is None:
        abort(404)
    return jsonify(quote.to_dict()), 200


@app.route("/authors/<int:author_id>/quotes", methods=["POST"])
def create_quote(author_id):
    author = AuthorModel.query.get(author_id)
    new_quote = request.json
    q = QuoteModel(author, new_quote["text"])
    db.session.add(q)
    db.session.commit()
    return jsonify(q.to_dict()), 201


@app.route("/quotes/<int:quote_id>", methods=['PUT'])
def edit_quote(quote_id):  # author text
    new_data = request.json
    quote = QuoteModel.query.get(quote_id)
    if quote is None:
        abort(404)
    # quote.text = new_data.get("text", quote.text)
    # quote.author = new_data.get("author", quote.author)
    for key, value in new_data.items():
        setattr(quote, key, value)
    db.session.commit()  # SQL --> UPDATE
    return jsonify(quote.to_dict()), 200


@app.route("/quotes/<int:quote_id>", methods=['DELETE'])
def delete(quote_id):
    quote = QuoteModel.query.get(quote_id)
    if quote is None:
        abort(404)
    db.session.delete(quote)
    db.session.commit()
    return f"Quote with id={quote_id} is deleted.", 200


if __name__ == "__main__":
    app.run(debug=True)
