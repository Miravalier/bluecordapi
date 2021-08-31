import asyncio
import aiohttp
import os
import requests
import smtplib
import concurrent.futures
from email.message import EmailMessage
from typing import Optional
from fastapi import FastAPI, Form
from pydantic import BaseModel, EmailStr
from starlette.responses import RedirectResponse


RECAPTCHA_URL = "https://www.google.com/recaptcha/api/siteverify"
RECAPTCHA_KEY = os.environ['RECAPTCHA_KEY']
ADMIN_EMAIL = os.environ['ADMIN_EMAIL']
SMTP_SERVER = os.environ['SMTP_SERVER']
SMTP_USER = os.environ['SMTP_USER']
SMTP_PASSWORD = os.environ['SMTP_PASSWORD']

EMAIL_SUBJECT = "Contact Form Submission (bluecordcomputing.com)"
EMAIL_TEMPLATE = "E-mail: {}\nCompany: {}\nMessage:\n-----\n{}\n-----"
EMAIL_TEMPLATE_HTML = """<html>
    <body>
        <p><b>E-mail:</b> {}</p>
        <p><b>Company:</b> {}</p>
        <p><b>Message:</b></p>
        <p>─────</p>
        <p>{}</p>
        <p>─────</p>
    </body>
</html>"""


app = FastAPI(root_path="/api")


def send_email(subject: str, text_content: str, html_content: str = None):
    # Create message
    email_message = EmailMessage()
    email_message['From'] = SMTP_USER
    email_message['To'] = ADMIN_EMAIL
    email_message['Subject'] = subject
    email_message.set_content(text_content)
    if html_content:
        email_message.add_alternative(html_content, subtype='html')

    # Send message
    with smtplib.SMTP_SSL(SMTP_SERVER) as smtp:
        smtp.login(user=SMTP_USER, password=SMTP_PASSWORD)
        smtp.send_message(email_message)


@app.post("/email")
async def post_email(
        email: EmailStr = Form(...),
        company: str = Form(...),
        message: str = Form(...),
        g_recaptcha_response: str = Form(..., alias='g-recaptcha-response')):

    # Check the recaptcha response
    try:
        async with aiohttp.ClientSession() as session:
            params = {"secret": RECAPTCHA_KEY, "response": g_recaptcha_response}
            async with session.post(RECAPTCHA_URL, params=params) as response:
                reply = await response.json()
        success = reply.get("success")
    except:
        success = False

    # Send the email if the recaptcha succeeds
    if success:
        loop = asyncio.get_running_loop()
        with concurrent.futures.ThreadPoolExecutor() as pool:
            await loop.run_in_executor(
                pool,
                send_email,
                EMAIL_SUBJECT,
                EMAIL_TEMPLATE.format(email, company, message)
                #EMAIL_TEMPLATE_HTML.format(email, company, message)
            )
    else:
        print("Recaptcha Failure")

    # Redirect the user to the thanks page with a GET request
    return RedirectResponse(url="/thanks.html", status_code=303)
