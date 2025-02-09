from flask import Flask, render_template, request, jsonify
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from twilio.rest import Client
import smtplib
from email.mime.text import MIMEText

app = Flask(__name__, static_folder='static')

# Google Sheets API Setup
SCOPE = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
CREDENTIALS_FILE = "service.json"  # Update with your credentials file path
SPREADSHEET_NAME = "USER DATA"

credentials = ServiceAccountCredentials.from_json_keyfile_name(CREDENTIALS_FILE, SCOPE)
gc = gspread.authorize(credentials)
sheet = gc.open(SPREADSHEET_NAME).sheet1  # Access first sheet

# Twilio API Credentials (Update with your Twilio credentials)
TWILIO_SID = "your_twilio_sid"
TWILIO_AUTH_TOKEN = "your_twilio_auth_token"
TWILIO_PHONE = "your_twilio_phone_number"

twilio_client = Client(TWILIO_SID, TWILIO_AUTH_TOKEN)

# Email Setup (Update with your Email credentials)
EMAIL_ADDRESS = "your_email@example.com"
EMAIL_PASSWORD = "your_email_password"
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587

def send_email(to_email, subject, body):
    msg = MIMEText(body)
    msg["Subject"] = subject
    msg["From"] = EMAIL_ADDRESS
    msg["To"] = to_email
    
    with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
        server.starttls()
        server.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
        server.sendmail(EMAIL_ADDRESS, to_email, msg.as_string())

def send_sms(to_number, message):
    twilio_client.messages.create(to=to_number, from_=TWILIO_PHONE, body=message)

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/registration')
def registration():
    return render_template('registration.html')

@app.route('/distress')
def distress():
    return render_template('distress.html')

@app.route('/register', methods=['POST'])
def register():
    data = request.json
    if not all(key in data for key in ["name", "age", "gender", "email", "latitude", "longitude", "guardian", "phone"]):
        return jsonify({"error": "Missing required fields"}), 400

    # Store data in Google Sheets
    sheet.append_row([data["name"], data["age"], data["gender"], data["email"], data["latitude"], data["longitude"], data["guardian"], data["phone"]])

    return jsonify({"message": "Registration successful!"})

@app.route('/sentdistress')
def distress_signal():
    print("ALERT: Distress signal sent!")  # Print an alert message in the console

    return jsonify({"message": "Distress signal sent!"}), 200

if __name__ == '__main__':
    app.run(debug=True)
