#!/usr/bin/env python3
"""
Resume Runner - sender.py
Prompts for an email + resume choice, sends via Gmail, logs the send.
"""

import os
import re
import json
import smtplib
from email.message import EmailMessage
from datetime import datetime, timezone

# ---------- CONFIG ----------
GMAIL_ADDRESS = "pratyuktpc@gmail.com"
GMAIL_APP_PASSWORD = "bakhrgibuwfhlqbi"  # generate at myaccount.google.com/apppasswords

SUBJECT = "DevOps Engineer Application – Pratyukt (2.7 Years Experience)"
BODY_TEMPLATE = """Dear {name},

I hope this message finds you well. I am writing to express my interest in the DevOps Engineer position at your organization.

I bring 2.7 years of hands-on experience in Kubernetes, CI/CD automation, AWS, and database high availability, with a strong focus on building reliable, scalable infrastructure. I have attached my resume for your consideration and would welcome the opportunity to discuss how my experience aligns with your team's requirements.

Thank you for your time and consideration. I look forward to hearing from you.

Best regards,
Pratyukt
7609991263 | linkedin.com/in/pratyukt-mohapatra-245304277 | github.com/PratyuktMohapatra
"""

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
RESUME_DIR = os.path.join(BASE_DIR, "resumes")
LOG_FILE = os.path.join(BASE_DIR, "log.json")
# -----------------------------


def load_log():
    if os.path.exists(LOG_FILE):
        with open(LOG_FILE, "r") as f:
            return json.load(f)
    return []


def save_log(log):
    with open(LOG_FILE, "w") as f:
        json.dump(log, f, indent=2)


def is_valid_email(email):
    return re.match(r"^[^@\s]+@[^@\s]+\.[^@\s]+$", email) is not None


def list_resumes():
    if not os.path.isdir(RESUME_DIR):
        os.makedirs(RESUME_DIR)
    files = [f for f in os.listdir(RESUME_DIR) if f.lower().endswith(".pdf")]
    return sorted(files)


def choose_resume():
    files = list_resumes()
    if not files:
        print(f"No PDF files found in {RESUME_DIR}. Add resumes there and try again.")
        return None
    print("\nAvailable resumes:")
    for i, f in enumerate(files, 1):
        print(f"  {i}. {f}")
    while True:
        choice = input("Pick a resume number: ").strip()
        if choice.isdigit() and 1 <= int(choice) <= len(files):
            return os.path.join(RESUME_DIR, files[int(choice) - 1])
        print("Invalid choice, try again.")


def send_email(to_email, resume_path, body):
    msg = EmailMessage()
    msg["Subject"] = SUBJECT
    msg["From"] = GMAIL_ADDRESS
    msg["To"] = to_email
    msg.set_content(body)

    with open(resume_path, "rb") as f:
        data = f.read()
    filename = os.path.basename(resume_path)
    msg.add_attachment(data, maintype="application", subtype="pdf", filename=filename)

    try:
        with smtplib.SMTP("smtp.gmail.com", 587) as server:
            server.starttls()
            server.login(GMAIL_ADDRESS, GMAIL_APP_PASSWORD)
            server.send_message(msg)
        return True, None
    except smtplib.SMTPAuthenticationError:
        return False, "Authentication failed - check your Gmail app password."
    except smtplib.SMTPException as e:
        return False, f"SMTP error: {e}"
    except OSError as e:
        return False, f"Network error (are you online?): {e}"


def main():
    print("=== Resume Runner - Send Application Email ===\n")

    # Get and validate email
    while True:
        to_email = input("Enter recipient email: ").strip()
        if is_valid_email(to_email):
            break
        print("That doesn't look like a valid email address. Try again.")

    # Company or HR name for greeting
    contact_name = input("Company or HR name (for greeting, e.g. 'Acme' or 'John'): ").strip()
    if not contact_name:
        contact_name = "there"
    body = BODY_TEMPLATE.format(name=contact_name)

    # Pick resume
    resume_path = choose_resume()
    if resume_path is None:
        return
    resume_name = os.path.basename(resume_path)

    # Dry run preview
    print("\n----- DRY RUN PREVIEW -----")
    print(f"To:      {to_email}")
    print(f"Subject: {SUBJECT}")
    print(f"Resume:  {resume_name}")
    print("Body:")
    print(body)
    print("----------------------------\n")

    confirm = input("Send this email? (y/n): ").strip().lower()
    if confirm != "y":
        print("Cancelled. Nothing was sent.")
        return

    ok, error = send_email(to_email, resume_path, body)

    log = load_log()
    entry = {
        "email": to_email,
        "contact_name": contact_name,
        "resume": resume_name,
        "sent_at": datetime.now(timezone.utc).isoformat(),
        "status": "sent" if ok else "failed",
        "replied": False,
        "followups_sent": 0,
    }
    log.append(entry)
    save_log(log)

    if ok:
        print(f"\n[SENT] Email sent to {to_email} with {resume_name} attached.")
    else:
        print(f"\n[FAILED] Could not send: {error}")
        print("This attempt was logged as 'failed' so you can retry later.")


if __name__ == "__main__":
    main()
