import requests
import random
import string
import time
from bs4 import BeautifulSoup
from fp.fp import FreeProxy
from stem import Signal
from stem.control import Controller

# कॉन्फ़िगरेशन सेटिंग्स
TARGET_URL = "https://your-website.com/register"  # अपना रजिस्ट्रेशन URL डालें
ATTEMPTS = 10  # कितने अटेम्प्ट करने हैं
TOR_MODE = True  # टॉर का उपयोग करें (सुनिश्चित करें कि टॉर इंस्टॉल है)
PROXY_MODE = False  # फ्री प्रॉक्सी का उपयोग करें
DELAY_BETWEEN_ATTEMPTS = 3  # सेकंड में

# यूजर-एजेंट लिस्ट
USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.0.3 Safari/605.1.15",
    "Mozilla/5.0 (X11; Linux x86_64; rv:89.0) Gecko/20100101 Firefox/89.0",
    "Mozilla/5.0 (iPhone; CPU iPhone OS 14_6 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.1.1 Mobile/15E148 Safari/604.1",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36 Edg/91.0.864.59"
]

def generate_random_email():
    """रैंडम ईमेल जनरेट करें"""
    domains = ["gmail.com", "yahoo.com", "hotmail.com", "outlook.com", "example.com"]
    username = ''.join(random.choices(string.ascii_lowercase + string.digits, k=random.randint(6, 12)))
    domain = random.choice(domains)
    return f"{username}@{domain}"

def generate_random_password(length=12):
    """रैंडम पासवर्ड जनरेट करें"""
    chars = string.ascii_letters + string.digits + string.punctuation
    return ''.join(random.choice(chars) for _ in range(length))

def get_random_user_agent():
    """रैंडम यूजर-एजेंट चुनें"""
    return random.choice(USER_AGENTS)

def get_tor_session():
    """टॉर के लिए नया सेशन बनाएं"""
    session = requests.Session()
    session.proxies = {'http': 'socks5h://localhost:9050', 'https': 'socks5h://localhost:9050'}
    return session

def renew_tor_connection():
    """टॉर IP एड्रेस बदलें"""
    with Controller.from_port(port=9051) as controller:
        controller.authenticate(password="your_tor_password")  # अपना टॉर पासवर्ड सेट करें
        controller.signal(Signal.NEWNYM)

def get_fresh_proxy():
    """नया प्रॉक्सी प्राप्त करें"""
    proxy = FreeProxy(rand=True, timeout=1).get()
    return {"http": proxy, "https": proxy}

def get_device_fingerprint():
    """रैंडम डिवाइस फिंगरप्रिंट जनरेट करें"""
    return {
        "screen_res": f"{random.randint(800, 3840)}x{random.randint(600, 2160)}",
        "timezone": random.choice(["GMT-5", "GMT+1", "GMT+5.5", "GMT+8", "GMT-8"]),
        "plugins": random.sample(["Chrome PDF Viewer", "Widevine Content Decryption Module", "Native Client"], random.randint(0, 3)),
        "platform": random.choice(["Win32", "Linux x86_64", "MacIntel"])
    }

def extract_csrf_token(html_content):
    """HTML से CSRF टोकन निकालें"""
    soup = BeautifulSoup(html_content, 'html.parser')
    token = None
    
    # सामान्य CSRF टोकन नामों के लिए चेक करें
    for name in ["csrf_token", "csrfmiddlewaretoken", "authenticity_token", "_token"]:
        token_element = soup.find(attrs={"name": name})
        if token_element and token_element.get("value"):
            token = token_element["value"]
            break
    
    return token

def attempt_registration(session, headers, fingerprint):
    """रजिस्ट्रेशन अटेम्प्ट करें"""
    try:
        # पहले पेज से CSRF टोकन प्राप्त करें
        response = session.get(TARGET_URL, headers=headers, timeout=10)
        csrf_token = extract_csrf_token(response.text)
        
        if not csrf_token:
            print("CSRF टोकन नहीं मिला. सुरक्षा कमजोर हो सकती है")
        
        # फॉर्म डेटा तैयार करें
        form_data = {
            "email": generate_random_email(),
            "password": generate_random_password(),
            "confirm_password": generate_random_password(),
            "username": ''.join(random.choices(string.ascii_lowercase, k=8)),
            "csrf_token": csrf_token,
            "fingerprint": str(fingerprint)
        }
        
        # रजिस्ट्रेशन रिक्वेस्ट भेजें
        response = session.post(TARGET_URL, data=form_data, headers=headers, timeout=15)
        
        # सफलता की जांच करें
        if response.status_code == 200:
            if "success" in response.text.lower() or "welcome" in response.text.lower():
                return True
        return False
        
    except Exception as e:
        print(f"त्रुटि: {str(e)}")
        return False

def run_security_test():
    """सुरक्षा परीक्षण चलाएं"""
    successful_registrations = 0
    
    for attempt in range(1, ATTEMPTS + 1):
        print(f"\nअटेम्प्ट #{attempt}/{ATTEMPTS}")
        
        # हेडर्स और फिंगरप्रिंट तैयार करें
        headers = {
            "User-Agent": get_random_user_agent(),
            "Accept-Language": random.choice(["en-US,en;q=0.9", "hi-IN;q=0.8", "mr-IN;q=0.7"]),
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8"
        }
        fingerprint = get_device_fingerprint()
        
        # सत्र सेटअप
        session = requests.Session()
        
        # IP रोटेशन
        if TOR_MODE:
            session = get_tor_session()
            renew_tor_connection()
            print("नया टॉर IP उपयोग कर रहा है")
        elif PROXY_MODE:
            session.proxies = get_fresh_proxy()
            print("नया प्रॉक्सी उपयोग कर रहा है")
        
        # रजिस्ट्रेशन अटेम्प्ट
        success = attempt_registration(session, headers, fingerprint)
        
        if success:
            successful_registrations += 1
            print("सफलता: खाता बनाया गया! सुरक्षा कमजोर है")
        else:
            print("विफलता: खाता नहीं बनाया जा सका")
        
        time.sleep(DELAY_BETWEEN_ATTEMPTS)
    
    # परिणाम रिपोर्ट
    print("\n" + "="*50)
    print(f"कुल सफल रजिस्ट्रेशन: {successful_registrations}/{ATTEMPTS}")
    print("="*50)
    
    if successful_registrations > 0:
        print("\n[सुरक्षा चेतावनी] आपकी सुरक्षा उपायों में कमजोरियां पाई गईं!")
        print("संभावित कारण:")
        print("1. IP प्रतिबंध पर्याप्त नहीं है")
        print("2. डिवाइस फिंगरप्रिंटिंग प्रभावी ढंग से लागू नहीं है")
        print("3. OTP सत्यापन को बायपास किया जा सकता है")
        print("4. दर सीमा पर्याप्त सख्त नहीं है")
        
        print("\nसुधार के उपाय:")
        print("1. व्यवहार विश्लेषण आधारित सुरक्षा लागू करें (उपयोगकर्ता व्यवहार पैटर्न की निगरानी)")
        print("2. मल्टी-फैक्टर ऑथेंटिकेशन को मजबूत करें")
        print("3. उन्नत कैप्चा सिस्टम लागू करें (जैसे reCAPTCHA v3)")
        print("4. रियल-टाइम थ्रेट डिटेक्शन सिस्टम लागू करें")
        print("5. ईमेल/फोन वेरिफिकेशन प्रक्रिया को मजबूत करें")
    else:
        print("\n[परिणाम] आपके सुरक्षा उपाय प्रभावी प्रतीत होते हैं!")

if __name__ == "__main__":
    print("सुरक्षा परीक्षण शुरू हो रहा है...")
    run_security_test()
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
