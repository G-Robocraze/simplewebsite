from flask import Flask, render_template, request, redirect, url_for
from flask_socketio import SocketIO, emit
import mysql.connector
import random
from threading import Thread
import time
from flask import current_app
app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app)

# Database connection details
db_host = 'localhost'
db_user = 'root'
db_password = 'Gsw@1924'
db_name = 'esamproject'

voltage1 = None
current1 = None
energy1 = None
voltage2 = None
current2 = None
energy2 = None
voltage3 = None
current3 = None
energy3 = None
# Function to validate user credentials
def validate_user(username, password):
    # Create a database connection
    conn = mysql.connector.connect(
        host=db_host,
        user=db_user,
        password=db_password,
        database=db_name
    )
    
    # Create a cursor object to execute SQL queries
    cursor = conn.cursor()
    
    # Execute the query to check if the user exists
    query = "SELECT * FROM users WHERE username = %s AND password = %s"
    cursor.execute(query, (username, password))
    
    # Fetch the result
    result = cursor.fetchone()
    
    # Close the cursor and database connection
    cursor.close()
    conn.close()
    
    # Return True if user exists, False otherwise
    if result:
        return True
    else:
        return False

@app.route('/')
def login():
    return render_template('login.html')

# Route to handle the login page
@app.route('/login', methods=['GET', 'POST'])
def handle_login():
    if request.method == 'POST':
        # Get the username and password from the form
        username = request.form['username']
        password = request.form['password']
        
        # Validate the user credentials
        if validate_user(username, password):
            return redirect(url_for('home'))
        else:
            return 'Invalid Credentials'
    else:
        return render_template('login.html')
        
@app.route('/home')
def home():
    return render_template('home.html')


@app.route('/receive_data', methods=['POST'])
def receive_data():
    global voltage1, current1, energy1, voltage2, current2, energy2, voltage3, current3, energy3
    data = request.get_json()
    print(data)  # Do something with the received data
    # Extract individual values
    voltage1 = data['voltage1']
    current1 = data['current1']
    energy1 = data['energy1']
    voltage2 = data['voltage2']
    current2 = data['current2']
    energy2 = data['energy2']
    voltage3 = data['voltage3']
    current3 = data['current3']
    energy3 = data['energy3']
    return 'Data received successfully'

def send_data():

    
    # Send random voltage, current, and energy values
    """ voltage1 = random.randint(220, 240)
    current1 = random.randint(1, 10)
    energy1 = voltage1 * current1
    voltage2 = random.randint(220, 240)
    current2 = random.randint(1, 10)
    energy2 = voltage2 * current2
    voltage3 = random.randint(220, 240)
    current3 = random.randint(1, 10)
    energy3 = voltage3 * current3 """
    global voltage1, current1, energy1, voltage2, current2, energy2, voltage3, current3, energy3
    
    conn = mysql.connector.connect(
        host=db_host,
        user=db_user,
        password=db_password,
        database=db_name
    )
    
    # Create a cursor object to execute SQL queries
    cursor = conn.cursor()
    
    # Execute the query to check if the user exists
    query = "INSERT INTO measurements (voltage1, current1, energy1, voltage2, current2, energy2, voltage3, current3, energy3 ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)"
    cursor.execute(query, (voltage1, current1, energy1, voltage2, current2, energy2, voltage3, current3, energy3))
    conn.commit()
    rowcount=cursor.rowcount
    print(f"{rowcount} row(s) affected")

    cursor.close()
    conn.close()

    data = {'voltage1': voltage1, 'current1': current1, 'energy1': energy1, 'voltage2': voltage2, 'current2': current2, 'energy2': energy2, 'voltage3': voltage3, 'current3': current3, 'energy3': energy3}
    with app.app_context():
        try:
            socketio.emit('data', data)
        except RuntimeError:
            current_app.logger.error('Unable to emit data to SocketIO clients.')
        time.sleep(2)
    # Schedule the next data send in 1 second
    socketio.start_background_task(send_data)

@socketio.on('connect')
def handle_connect():
    print('Client connected')
    t = Thread(target=send_data)
    t.daemon = True
    t.start()



if __name__ == '__main__':
    socketio.run(app, debug=True)

