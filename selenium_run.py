from game2048 import create_app, db, socketio
from config import SeleniumTestConfig
from game2048.models import User, Match

app = create_app(SeleniumTestConfig)

if __name__ == "__main__":
    socketio.run(app, debug=True)