from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from datetime import datetime
import time
import smtplib
from email.message import EmailMessage
import os
import undetected_chromedriver as uc


# ==== Credentials from GitHub Secrets ====
user_email = os.getenv("USER_EMAIL")
user_pass = os.getenv("USER_PASS")
sender_email = os.getenv("SENDER_EMAIL")
sender_app_password = os.getenv("EMAIL_PASSWORD")

def send_email_notification(receiver_email):
    msg = EmailMessage()
    msg['Subject'] = '✅ VPT Punch-Out Successful'
    msg['From'] = sender_email
    msg['To'] = receiver_email
    msg.set_content(f'''Hi Ak,

Your punch-out was successful on VPT Dashboard at {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}.

- Akku''')

    try:
        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
            smtp.login(sender_email, sender_app_password)
            smtp.send_message(msg)
        print(f"📧 Email sent to {receiver_email}")
    except Exception as e:
        print("❌ Failed to send email:", str(e))

# ==== Headless Chrome Driver ====
options = uc.ChromeOptions()
options.headless = True
options.add_argument('--no-sandbox')
options.add_argument('--disable-dev-shm-usage')

# ✅ Force version 135 to match GitHub's Chrome version
driver = uc.Chrome(options=options, version_main=135)

try:
    driver.get("https://vptdashboard.com/VptLogin/")

    WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.NAME, "Email")))
    driver.find_element(By.NAME, "Email").send_keys(user_email)
    driver.find_element(By.NAME, "Password").send_keys(user_pass)
    driver.find_element(By.ID, "signIn").click()

    WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR, ".nav-link.dropdown-toggle")))
    print(f"✅ Signed in as: {user_email}")

    attendance_link = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.CSS_SELECTOR, "a[href*='Markattendance/UpdateAttendanceDetails']"))
    )
    attendance_link.click()

    punch_out_btn = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.CSS_SELECTOR, "input[value*='Punch Out']"))
    )
    punch_out_btn.click()

    ok_btn = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.CSS_SELECTOR, "button[class*='swal-button--confirm']"))
    )
    ok_btn.click()

    time.sleep(3)
    print("✅ Punch out successful")

    send_email_notification(user_email)

except Exception as e:
    print("❌ Something went wrong:", str(e))

finally:
    time.sleep(3)
    driver.quit()
