from game2048 import create_app, socketio, db
from config import SeleniumTestConfig

app = create_app(SeleniumTestConfig)

if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    socketio.run(app)
