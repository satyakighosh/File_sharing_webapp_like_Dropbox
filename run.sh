sudo systemctl start mongod
export FLASK_ENV=development 
export FLASK_APP=server.py

source venv/bin/activate

flask run
