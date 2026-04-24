import smtplib
import os
from email.message import EmailMessage
import mimetypes

def send_job_alert(company_name, job_title, job_link, resume_path):
    # Fetch credentials from environment variables for security
    sender_email = os.environ.get("SENDER_EMAIL")
    sender_password = os.environ.get("SENDER_PASSWORD")
    
    # We will just send the email to yourself, but you could change this!
    receiver_email = "iamajayluhar@gmail.com" 

    if not sender_email or not sender_password:
        print("\n[Email] Skipping email step: SENDER_EMAIL or SENDER_PASSWORD not set in terminal.")
        return

    print(f"[Email] Preparing email alert for {company_name}...")

    # 1. Setup the basic email content
    msg = EmailMessage()
    msg['Subject'] = f"🚀 New Job Alert: {job_title} at {company_name}"
    msg['From'] = sender_email
    msg['To'] = receiver_email

    body = f"""
    Hello!

    Your AI Agent has found a new job match and tailored your resume.

    🏢 Company: {company_name}
    💼 Role: {job_title}
    🔗 Apply Link: {job_link}

    Your customized Word document resume is attached. Good luck!
    """
    msg.set_content(body)

    # 2. Attach the generated Word document
    if os.path.exists(resume_path):
        with open(resume_path, 'rb') as f:
            file_data = f.read()
            file_name = os.path.basename(resume_path)
        
        # Determine the file type so the email client knows it's a docx
        ctype, encoding = mimetypes.guess_type(resume_path)
        if ctype is None or encoding is not None:
            ctype = 'application/octet-stream'
        maintype, subtype = ctype.split('/', 1)

        msg.add_attachment(file_data, maintype=maintype, subtype=subtype, filename=file_name)
    else:
        print(f"[Email] Warning: Attachment not found at {resume_path}")

    # 3. Connect to the SMTP server and send
    try:
        # Port 465 is for SSL connection
        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
            smtp.login(sender_email, sender_password)
            smtp.send_message(msg)
        print(f"[Email] SUCCESS! Alert sent to {receiver_email}")
    except Exception as e:
        print(f"[Email] Failed to send email: {e}")