from flask import Flask
from flask import url_for, redirect, render_template, request, send_from_directory
from flask_sqlalchemy import SQLAlchemy
from werkzeug.utils import secure_filename
import os

app = Flask(__name__)


app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///img.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)


class DataBase(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.Text, nullable=False)
    data = db.Column(db.LargeBinary, nullable=False)


@app.route('/')
def home():
    return render_template('idx.html')


@app.route('/upload', methods=['POST'])
def upload():
    pic = request.files['img']
    if not pic:
        return 'No image uploaded!', 400

    secure = secure_filename(pic.filename)
    pic.save(os.path.join('static', secure))
    new_item = DataBase(name=secure, data=pic.read())
    db.session.add(new_item)
    db.session.commit()
    return redirect(url_for('photos'))


@app.route('/photoview/')
def photos():
    album = DataBase.query.all()
    return render_template('photoview.html', album=album)


def find_valid_id(id):
    picture = DataBase.query.filter_by(id=id).first()
    if not picture:
        picture = DataBase.query.filter_by(id=id+1).first()
    if picture is None:
        try:
            return find_valid_id(id+1)
        except RecursionError:
            return 'Nothing to delete maybe try uploading some files', 404
    return picture


@app.route('/delete/<int:id>')
def delete(id):
    picture = find_valid_id(id)
    if len(DataBase.query.all()) == 0:
        return 'Nothing to delete', 404
    try:
        os.remove(os.path.join('static', picture.name))
    except FileNotFoundError:
        pass
    db.session.delete(picture)
    db.session.commit()
    return redirect(url_for('photos'))


if __name__ == '__main__':
    app.run(debug=True)
