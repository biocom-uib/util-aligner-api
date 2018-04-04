import smtplib
import csv
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from email import encoders
from email.mime.base import MIMEBase
from os import unlink
from tempfile import NamedTemporaryFile
from config import config

EMAIL_FROM = config['EMAIL_FROM']
EMAIL_PASSWORD = config['EMAIL_PASSWORD']


def write_results(results):
    with NamedTemporaryFile(delete=False, mode='w') as tmpfile:
        writer = csv.writer(tmpfile)
        writer.writerows(results)
        return tmpfile.name


def send_email(data, results, emails):
    def _send_email(email):
        msg = MIMEMultipart()
        msg['Subject'] = 'Alignment Finished'
        msg['From'] = EMAIL_FROM
        msg.preamble = 'Results for alignment'
        body = f"Results for align {data['net1']} with {data['net2']} using {data['aligner']}"
        body += str(results)
        msg.attach(MIMEText(body))
        msg.attach(record)
        msg['To'] = email
        server.send_message(msg)
    tmp_file = write_results(results.get('results', {}).get('alignment', [{}]))

    with open(tmp_file) as fp:
        record = MIMEBase('application', 'octet-stream')
        record.set_payload(fp.read())
        encoders.encode_base64(record)
        record.add_header('Content-Disposition', 'attachment',
                          filename='Alignment.csv')
    unlink(tmp_file)
    server = smtplib.SMTP('smtp.gmail.com', 587)
    server.ehlo()
    server.starttls()
    server.login(EMAIL_FROM, EMAIL_PASSWORD)
    list(map(_send_email, emails))
    server.quit()
