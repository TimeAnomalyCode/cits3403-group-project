from game2048 import create_app, socketio
from config import SeleniumTestConfig

app = create_app(SeleniumTestConfig)

if __name__ == "__main__":
    socketio.run(app)
