import sqlalchemy as sa
import sqlalchemy.orm as so

# from game2048 import app
from game2048 import create_app, db, socketio
from game2048.models import User, Match

# Use Ctrl + Shift + R to hard refresh browser
app = create_app()


# using 'flask shell' will load all the context you need
@app.shell_context_processor
def make_shell_context():
    return {"sa": sa, "so": so, "db": db, "User": User, "Match": Match}


# using default vscode debugger to step through each line
if __name__ == "__main__":
    socketio.run(app)
