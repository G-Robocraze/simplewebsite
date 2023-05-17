from flask import Flask, render_template, request, redirect, url_for
from flask_socketio import SocketIO, emit
import mysql.connector
import random, json
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

data = {'voltage1': 220, 'current1': 3, 'energy1': 660, 'voltage2': 230, 'current2': 7, 'energy2': 1610, 'voltage3': 225, 'current3': 2, 'energy3': 450}
state={'button_id':'load1', 'status':'OFF'}
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
    global data
    data = request.get_json()
    print(data)  # Do something with the received data
    # Extract individual values
    return 'Data received successfully'

def send_data():
    # Send random voltage, current, and energy values
    global data
    voltage1 = data['voltage1']
    current1 = data['current1']
    energy1 = data['energy1']
    voltage2 = data['voltage2']
    current2 = data['current2']
    energy2 = data['energy2']
    voltage3 = data['voltage3']
    current3 = data['current3']
    energy3 = data['energy3']
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

    #data = {'voltage1': voltage1, 'current1': current1, 'energy1': energy1, 'voltage2': voltage2, 'current2': current2, 'energy2': energy2, 'voltage3': voltage3, 'current3': current3, 'energy3': energy3}
    with app.app_context():
        try:
            socketio.emit('data', data)
        except RuntimeError:
            current_app.logger.error('Unable to emit data to SocketIO clients.')
        time.sleep(5)
    # Schedule the next data send in 1 second
    socketio.start_background_task(send_data)

@socketio.on('connect')
def handle_connect():
    print('Client connected')
    t1 = Thread(target=send_data)
    t1.daemon = True
    t1.start()

@socketio.on('send_status')
def handle_send_status(state):
    button_id = state['button_id']
    status=state['status']
    # Process the received status
    # For example:
    if button_id == 'load1':
        # Do something for Load 1 with the received status
        pass
    elif button_id == 'load2':
        # Do something for Load 2 with the received status
        pass
    elif button_id == 'load3':
        # Do something for Load 3 with the received status
        pass
    conn = mysql.connector.connect(
        host=db_host,
        user=db_user,
        password=db_password,
        database=db_name
    )
    cursor = conn.cursor()
    query = "UPDATE loads SET state = %s WHERE Load_id = %s"
    cursor.execute(query, (status, button_id))
    conn.commit()
    cursor.close()
    conn.close()
    print(state)

@socketio.on('list_order')
def handle_list_order(jsonData):
    data_list = json.loads(jsonData)
    conn = mysql.connector.connect(
        host=db_host,
        user=db_user,
        password=db_password,
        database=db_name
    )
    cursor = conn.cursor()
    query = "UPDATE priority SET Load_id = %s WHERE id = %s"
    # Iterate over the data_list and update each row in the table
    for i, item in enumerate(data_list, start=1):
        cursor.execute(query, (item, i))
    conn.commit()
    cursor.close()
    conn.close()
    # Process the received list order data
    # For example, you can print it or perform any other desired action
    print(data_list)


if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0', port=5000, debug=True)

