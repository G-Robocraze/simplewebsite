import requests
import random
import time

def send_data():
    while True:
        # Generate random data
        voltage1 = random.randint(220, 240)
        current1 = random.randint(1, 10)
        energy1 = voltage1 * current1
        voltage2 = random.randint(220, 240)
        current2 = random.randint(1, 10)
        energy2 = voltage2 * current2
        voltage3 = random.randint(220, 240)
        current3 = random.randint(1, 10)
        energy3 = voltage3 * current3

        data = {
            'voltage1': voltage1,
            'current1': current1,
            'energy1': energy1,
            'voltage2': voltage2,
            'current2': current2,
            'energy2': energy2,
            'voltage3': voltage3,
            'current3': current3,
            'energy3': energy3
        }

        # Send the data to the Flask server
        url = 'http://localhost:5000/receive_data'
        response = requests.post(url, json=data)

        if response.status_code == 200:
            print('Data sent successfully')
        else:
            print('Failed to send data')

        time.sleep(5)  # Delay for 2 seconds before sending the next data

if __name__ == '__main__':
    send_data()
