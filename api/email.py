import smtplib

from email.message import EmailMessage
from email import encoders
from email.mime.base import MIMEBase
import os

def send_email(data, results, emails):
    def _send_email(email):
        msg['To'] = email
        server.sendmail(EMAILFROM, email, msg.as_string()) 


    msg = EmailMessage()
    msg['Subject'] = "Results of util-aligner"
    msg['From'] = EMAILFROM
    msg.preamble = f""" Results for align 
                        {data['input_network']} with {data['output_network']}
                        using {data['aligner']}
    """
    tmp_file = write_results(results)
    with open(tmp_file) as fp:
        record = MIMEBase('application', 'octet-stream')
        record.set_payload(fp.read())
        encoders.encode_base64(record)
        record.add_header('Content-Disposition', 'attachment',
                          filename=os.path.basename(tmp_file))
    msg.attach(record)
    server = smtplib.SMTP('smtp.gmail.com', 587)
    server.ehlo()
    server.starttls()
    server.login(EMAILFROM, 'password')
    map(_send_email, emails)
    server.quit()

 