import sqlalchemy as sa
import sqlalchemy.orm as so
from game2048 import app, db
from game2048.models import User

# Use Ctrl + Shift + R to hard refresh browser

# using 'flask shell' will load all the context you need
@app.shell_context_processor
def make_shell_context():
    return {'sa': sa, 'so': so, 'db': db, 'User': User}

# using default vscode debugger to step through programs
if __name__ == "__main__":
    app.run()