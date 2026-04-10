import sqlalchemy as sa
import sqlalchemy.orm as so
from game2048 import app

# Use Ctrl + Shift + R to hard refresh browser

# using 'flask shell' will load all the context you need
@app.shell_context_processor
def make_shell_context():
    return {'sa': sa, 'so': so}

# using default vscode debugger to step through each line
if __name__ == "__main__":
    app.run()