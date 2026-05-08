# 2048 Multiplayer
> 2048 is a game about moving tiles and combining them in powers of 2. We were inspired by Tetris 99 to battle opponents letting you attack opponents as you race to build points.
# Group Members
| UWA ID | Name | Github Username |
| --- | --- | --- |
| 24599992 | Aiman Hakimin Bin Ahmad Khairi | TimeAnomalyCode |
| 24377984 | Wentao Luo | LarkVenter |
| 24991966 | Chi Hin Elvis Suen | elvis1126-student |
| 24262394 | James Shirley | 24262394 |
# Setup and Run Code
1. Clone the repository
```
git clone https://github.com/TimeAnomalyCode/cits3403-group-project.git
```
2. Create a virtual environment in the project directory
```
python -m venv .venv
```
3. Activate the virtual environment
```
.venv\Scripts\activate
```
4. Install libraries
```
pip install -r requirements.txt
```
5. Setup Database
```
flask db upgrade
```
6. Add .env to the base directory with the following variables
```
MAIL_SERVER = 
MAIL_PORT = 
MAIL_USERNAME = 
MAIL_PASSWORD = 
MAIL_USE_TLS = 
MAIL_USE_SSL = 
SECRET_KEY = 
SQLALCHEMY_DATABASE_URI = 
MAIL_DEFAULT_SENDER_NAME = 
MAIL_DEFAULT_SENDER_ADDRESS = 
```
7. Run the web app
```
flask run
```
# Run Tests
## Unit Tests
```
pytest testing/  --cov=game2048 --cov-report=term
```
## Selenium Tests
### Account Test
```
pytest testing/Selenium_testing.py  --cov=game2048 --cov-append --cov-report=html
```
### Game Test
```
pytest testing/Selenium_test_game.py --cov=game2048 --cov-append --cov-report=html
```
# Formatting and Linting and QOL
## VS Code Extensions
1. Code Spell Checker: To prevent typos
2. Jinja: To have Jinja language support when working in HTML
3. djLint: To format and lint HTML and Jinja
4. Error Lens: To see errors in JS early
5. HTML CSS Support: To have autocomplete with CSS
6. Prettier: To format and lint JS and CSS
7. Python: To have Python language support
8. Ruff: To format and lint Python
9. SQLite Viewer: To view SQLite Database
