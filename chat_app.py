from flask import Flask, render_template, request
from flask_socketio import SocketIO, emit
from flask_sqlalchemy import SQLAlchemy


app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///chatroom.db" #he calls it db001
db = SQLAlchemy(app)

class User(db.Model):
    id = db.Column(db.String, primary_key=True)
    username = db.Column(db.String, unique=True, nullable=False)
    colour = db.Column(db.String)

class Chats(db.Model):
    cid = db.Column(db.Integer, primary_key=True)
    cmessage = db.Column(db.String, nullable=False)
    cuser = db.Column(db.Integer, db.ForeignKey(User.id))

with app.app_context():
    db.create_all()


users = {}
#this will eventually go in the database
userColours = {}

@app.route("/")
def home():
    return render_template("index.html")

@socketio.on('connect')
def handle_connect():
    print("client connected")

@socketio.on("user_join")
def handle_user_join(data):
    print(f"User {data['username']} joined!")
    users[data['username']] = request.sid
    userColours[data['username']] = data['colour']

    user = User(
        username=data["username"],
        colour=data["colour"],
        id = users[data['username']]
    )
    db.session.add(user)
    db.session.commit()


@socketio.on('new_message')
def handle_new_message(message):
    print(f"New message: {message}")
    username = None 
    for user in users:
        if users[user] == request.sid:
            username = user
    emit("chat", {"message": message, "username": username, "colour": userColours[username]}, broadcast=True)    #broadcast message to everyone conected to chat

if __name__ == "__main__":
    socketio.run(app)
