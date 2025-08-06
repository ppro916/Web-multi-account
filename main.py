import requests
import random
import string
import time

# --- Telegram Config ---
TELEGRAM_BOT_TOKEN = "8474861805:AAGk_7SHh-x4fBF5exgixQXUWg2TVuuR_W0"
CHAT_ID = "7991797378"

# Temporary email generate
def generate_temp_email():
    username = ''.join(random.choices(string.ascii_lowercase + string.digits, k=10))
    domain = "1secmail.com"
    email = f"{username}@{domain}"
    return email, username, domain

# OTP Fetch
def fetch_otp(username, domain):
    print(f"[📬] Checking inbox for {username}@{domain}...")
    for i in range(10):
        url = f"https://www.1secmail.com/api/v1/?action=getMessages&login={username}&domain={domain}"
        resp = requests.get(url).json()
        if resp:
            mail_id = resp[0]['id']
            mail_content_url = f"https://www.1secmail.com/api/v1/?action=readMessage&login={username}&domain={domain}&id={mail_id}"
            mail = requests.get(mail_content_url).json()
            print("[📨] Email subject:", mail['subject'])
            print("[📨] Email body:\n", mail['body'])

            # OTP guessing (6 digit number)
            otp = ''.join(filter(str.isdigit, mail['body']))
            print(f"[🔢] OTP Extracted: {otp}")
            return otp
        time.sleep(2)
    print("[❌] OTP not received in time.")
    return None

# File + Telegram Save
def save_and_send(email, password):
    text = f"📧 Email: {email}\n🔑 Password: {password}\n---------------------------"
    
    # Save locally
    with open("accounts_saved.txt", "a") as f:
        f.write(text + "\n")
    print("[💾] File saved locally.")

    # Send via Telegram
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": CHAT_ID,
        "text": text
    }
    res = requests.post(url, data=payload)
    if res.status_code == 200:
        print("[📤] Sent to Telegram successfully.")
    else:
        print("[❌] Failed to send Telegram message.")

# Main
if __name__ == "__main__":
    email, username, domain = generate_temp_email()
    password = "Test@1234"
    
    print(f"[🧪] Temp email generated: {email}")
    save_and_send(email, password)

    print("\n[👉] या email ने वेबसाइटवर अकाउंट बनव. तयार झाल्यावर Enter दाब.")
    input("➡️ Done? Press Enter to fetch OTP...\n")

    otp = fetch_otp(username, domain)
    if otp:
        print(f"[✅] OTP fetched: {otp}")
    else:
        print("[⚠️] Verification failed.")
