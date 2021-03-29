from smtplib import SMTP
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from asyncio import sleep as asyncio_sleep
from config import config

from jinja2 import Environment, FileSystemLoader, select_autoescape


BASE_URL = config['SERVER_URL'] + config['BASE_PATH']
EMAIL_FROM = config['EMAIL_FROM']
EMAIL_PASSWORD = config['EMAIL_PASSWORD']

JINJA2_ENV = Environment(
    loader = FileSystemLoader('/opt/templates'),
    autoescape = select_autoescape(['html', 'xml'])
)


async def send_email_alignment(response, emails):
    await send_email(
        response,
        emails,
        subject = f"Alignment with {response['aligner']} finished",
        template_name = 'email-alignment-response.html.j2'
    )

async def send_email_comparison(response, emails):
    await send_email(
        response,
        emails,
        subject = "Alignment comparison finished",
        template_name = 'email-comparison-response.html.j2'
    )


async def send_email(response, emails, subject, template_name):
    template = JINJA2_ENV.get_template(template_name)

    email_body = template.render(**response, base_url=BASE_URL)

    inline_files = []
    attachments = []

    def _send_email(email):
        msg = MIMEMultipart('mixed')
        msg['Subject'] = subject
        msg['From'] = EMAIL_FROM
        msg['To'] = email

        body = MIMEMultipart('related')
        body.attach(MIMEText(email_body, 'html'))

        msg.attach(body)
        server.send_message(msg)

    server = SMTP('smtp.gmail.com', 587)
    server.ehlo()
    server.starttls()
    server.login(EMAIL_FROM, EMAIL_PASSWORD)
    list(map(_send_email, emails))
    server.quit()

    print(f"sent {subject}")
