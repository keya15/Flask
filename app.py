from flask import Flask, jsonify, request, make_response
from flask_sqlalchemy import SQLAlchemy
from marshmallow_sqlalchemy import SQLAlchemySchema
from marshmallow import fields

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://keya:keya15@localhost:3306/testdb'
db = SQLAlchemy(app)

class Authors(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(20))
    specialisation = db.Column(db.String(50))

    def create(self):
        db.session.add(self)
        db.session.commit()
        return self

    def __init__(self, name, specialisation):
        self.name = name
        self.specialisation = specialisation

@app.before_first_request
def setup():
    #create table-Authors
    db.create_all()

class AuthorSchema(SQLAlchemySchema):
    class Meta(SQLAlchemySchema.Meta):
        model = Authors
        sql_session = db.session

    id = fields.Number(dump_only=True)
    name = fields.String(required=True)
    specialisation = fields.String(required=True)

@app.route('/authors', methods=['GET'])
def index():
    get_authors = Authors.query.all()
    author_schema = AuthorSchema(many=True)
    authors = author_schema.dump(get_authors)
    return make_response(jsonify({"authors": authors}))

@app.route('/authors/<id>', methods=['GET'])
def get_author_id(id):
    get_authors = Authors.query.get(id)
    author_schema = AuthorSchema()
    author = author_schema.dump(get_authors)
    return make_response(jsonify({"author": author}))

@app.route('/authors', methods=['POST'])
def create_author():
    data = request.get_json()
    author_schema = AuthorSchema()
    result = Authors(name=data['name'], specialisation=data['specialisation']).create()
    auth = author_schema.dump(result)
    return make_response(jsonify({"author": auth}), 201)

@app.route('/authors/<id>', methods=['PUT'])
def update_author_by_id(id):
    data = request.get_json()
    get_author = Authors.query.get(id)
    if data.get('name'):
        get_author.name = data['name']
    if data.get('specialisation'):
        get_author.specialisation = data['specialisation']
    db.session.add(get_author)
    db.session.commit()
    author_schema = AuthorSchema()
    author = author_schema.dump(get_author)
    return make_response(jsonify({"authors": author}))

@app.route('/authors/<id>', methods=['DELETE'])
def delete_author_by_id(id):
    get_author = Authors.query.get(id)
    db.session.delete(get_author)
    db.session.commit()
    return make_response("", 204)    


if __name__ == "__main__":
    app.run(debug=True)