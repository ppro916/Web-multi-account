import requests
import random
import string
import time
from bs4 import BeautifulSoup
from fp.fp import FreeProxy
from stem import Signal
from stem.control import Controller

# कॉन्फ़िगरेशन सेटिंग्स
TARGET_URL = "https://your-website.com/register"  # ← इथे तुझं registration URL टाक
ATTEMPTS = 10
TOR_MODE = True
PROXY_MODE = False
DELAY_BETWEEN_ATTEMPTS = 3

# Telegram कॉन्फिग (तुझं बोट टोकन आणि Chat ID टाक)
TELEGRAM_BOT_TOKEN = "8474861805:AAGk_7SHh-x4fBF5exgixQXUWg2TVuuR_W0"
CHAT_ID = "7991797378"

# यूजर एजंट्स
USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36...",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15...",
    "Mozilla/5.0 (X11; Linux x86_64; rv:89.0)...",
    "Mozilla/5.0 (iPhone; CPU iPhone OS 14_6 like Mac OS X)...",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64)..."
]

def generate_random_email():
    domains = ["gmail.com", "yahoo.com", "hotmail.com", "outlook.com", "example.com"]
    username = ''.join(random.choices(string.ascii_lowercase + string.digits, k=random.randint(6, 12)))
    domain = random.choice(domains)
    return f"{username}@{domain}"

def generate_temp_email():
    domains = ["gmail.com", "yahoo.com", "hotmail.com", "outlook.com", "example.com"]
    username = ''.join(random.choices(string.ascii_lowercase + string.digits, k=random.randint(6, 12)))
    domain = random.choice(domains)
    email = f"{username}@{domain}"
    return email, username, domain

def fetch_otp(username, domain):
    # ← हे demo function आहे. TEMP mail वापरत असशील तर इथे email API call कर
    return ''.join(random.choices(string.digits, k=6))

def generate_random_password(length=12):
    chars = string.ascii_letters + string.digits + string.punctuation
    return ''.join(random.choice(chars) for _ in range(length))

def get_random_user_agent():
    return random.choice(USER_AGENTS)

def get_tor_session():
    session = requests.Session()
    session.proxies = {
        'http': 'socks5h://localhost:9050',
        'https': 'socks5h://localhost:9050'
    }
    return session

def renew_tor_connection():
    with Controller.from_port(port=9051) as controller:
        controller.authenticate()  # जर पासवर्ड नसेल तर हेच ठेव
        controller.signal(Signal.NEWNYM)

def get_fresh_proxy():
    proxy = FreeProxy(rand=True, timeout=1).get()
    return {"http": proxy, "https": proxy}

def get_device_fingerprint():
    return {
        "screen_res": f"{random.randint(800, 3840)}x{random.randint(600, 2160)}",
        "timezone": random.choice(["GMT-5", "GMT+1", "GMT+5.5", "GMT+8", "GMT-8"]),
        "plugins": random.sample(["Chrome PDF Viewer", "Widevine", "Native Client"], random.randint(0, 3)),
        "platform": random.choice(["Win32", "Linux x86_64", "MacIntel"])
    }

def extract_csrf_token(html_content):
    soup = BeautifulSoup(html_content, 'html.parser')
    token = None
    for name in ["csrf_token", "csrfmiddlewaretoken", "authenticity_token", "_token"]:
        token_element = soup.find(attrs={"name": name})
        if token_element and token_element.get("value"):
            token = token_element["value"]
            break
    return token

def attempt_registration(session, headers, fingerprint):
    try:
        response = session.get(TARGET_URL, headers=headers, timeout=10)
        csrf_token = extract_csrf_token(response.text)

        if not csrf_token:
            print("⚠️ CSRF टोकन सापडला नाही. सुरक्षा ढिल असू शकते.")

        form_data = {
            "email": generate_random_email(),
            "password": generate_random_password(),
            "confirm_password": generate_random_password(),
            "username": ''.join(random.choices(string.ascii_lowercase, k=8)),
            "csrf_token": csrf_token,
            "fingerprint": str(fingerprint)
        }

        response = session.post(TARGET_URL, data=form_data, headers=headers, timeout=15)

        if response.status_code == 200 and ("success" in response.text.lower() or "welcome" in response.text.lower()):
            return True

        return False

    except Exception as e:
        print(f"❌ त्रुटि: {str(e)}")
        return False

def save_and_send(email, password):
    text = f"📧 Email: {email}\n🔑 Password: {password}\n---------------------------"

    with open("accounts_saved.txt", "a") as f:
        f.write(text + "\n")
    print("[💾] File saved locally.")

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

def run_security_test():
    successful_registrations = 0

    for attempt in range(1, ATTEMPTS + 1):
        print(f"\nअटेम्प्ट #{attempt}/{ATTEMPTS}")

        headers = {
            "User-Agent": get_random_user_agent(),
            "Accept-Language": random.choice(["en-US,en;q=0.9", "hi-IN;q=0.8"]),
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8"
        }
        fingerprint = get_device_fingerprint()

        session = requests.Session()

        if TOR_MODE:
            session = get_tor_session()
            renew_tor_connection()
            print("🔁 नया Tor IP उपयोग हो रहा है")
        elif PROXY_MODE:
            session.proxies = get_fresh_proxy()
            print("🌐 नया प्रॉक्सी उपयोग हो रहा है")

        success = attempt_registration(session, headers, fingerprint)

        if success:
            successful_registrations += 1
            print("✅ खाता बन गया! सुरक्षा कमजोर आहे.")
        else:
            print("❌ खाता बनवता आला नाही")

        time.sleep(DELAY_BETWEEN_ATTEMPTS)

    print("\n" + "="*50)
    print(f"कुल सफल रजिस्ट्रेशन: {successful_registrations}/{ATTEMPTS}")
    print("="*50)

    if successful_registrations > 0:
        print("\n[⚠️ सुरक्षा चेतावनी] तुमच्या वेबसाईटवर सुरक्षा कमकुवत आहे.")
    else:
        print("\n✅ तुमचे सुरक्षा उपाय प्रभावी दिसत आहेत!")

# ------------------------
# Test Part (Manual Email)
# ------------------------

if __name__ == "__main__":
    print("सुरक्षा परीक्षण शुरू हो रहा है...\n")
    run_security_test()

    email, username, domain = generate_temp_email()
    password = "Test@1234"
    print(f"[🧪] Temp email generated: {email}")
    save_and_send(email, password)

    input("\n[👉] या email ने वेबसाइटवर अकाउंट बनव. तयार झाल्यावर Enter दाब.\n➡️ Done? Press Enter to fetch OTP...\n")

    otp = fetch_otp(username, domain)
    if otp:
        print(f"[✅] OTP fetched: {otp}")
    else:
        print("[⚠️] Verification failed.")
