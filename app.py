from flask import Flask, jsonify, abort, request, g
from pathlib import Path
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

# Документация по миграциям: https://flask-migrate.readthedocs.io/en/latest/

BASE_DIR = Path(__file__).parent

app = Flask(__name__)
app.config['JSON_AS_ASCII'] = False
app.config['SQLALCHEMY_DATABASE_URI'] = f"sqlite:///{BASE_DIR / 'main.db'}"
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


@app.route("/quotes", methods=["POST"])
def create_quote():
    quote_data = request.json
    # quote = QuoteModel(author=quote_data["author"], text=quote_data["text"])
    quote = QuoteModel(**quote_data)
    db.session.add(quote)
    db.session.commit()
    return jsonify(quote.to_dict()), 201


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
