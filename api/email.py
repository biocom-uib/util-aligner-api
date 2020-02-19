from smtplib import SMTP
from email import encoders
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from asyncio import sleep as asyncio_sleep
from bson.objectid import ObjectId
from csv import writer as csv_writer
from os import unlink
from tempfile import NamedTemporaryFile
from config import config

from jinja2 import Environment, FileSystemLoader, select_autoescape

from matplotlib import use as matplotlib_use
matplotlib_use('Agg')
from matplotlib.pyplot import figure as matplotlib_figure, close as matplotlib_close
from seaborn import set as seaborn_set
seaborn_set()

BASE_URL = config['SERVER_URL'] + config['BASE_PATH']
EMAIL_FROM = config['EMAIL_FROM']
EMAIL_PASSWORD = config['EMAIL_PASSWORD']

JINJA2_ENV = Environment(
    loader = FileSystemLoader('/opt/templates'),
    autoescape = select_autoescape(['html', 'xml'])
)


async def prepare_attachment_tsv(mongo_gridfs, response, obj, key, header=None):
    value = obj.get(key)

    ## now sent as a link
    if value is None or isinstance(value, dict) and 'file' in value:
        return {}

    with NamedTemporaryFile(delete=False, mode='w', suffix='.tmp.tsv') as tmpfile:
        writer = csv_writer(tmpfile, delimiter='\t')

        if header is None:
            writer.writerows(value)
        elif len(header) > 1:
            writer.writerow(header)
            writer.writerows(value)
        else:
            writer.writerows((item,) for item in value)

        tmpfile_name = tmpfile.name

    return {key+'.tsv': (tmpfile_name, False, ('text', 'csv'))}


async def write_ec_data(response, scores_key, mongo_gridfs):
    files = {}

    scores = response[scores_key]
    ec_data = scores['ec_data']

    files.update(
        await prepare_attachment_tsv(mongo_gridfs, response, ec_data, 'non_preserved_edges', header=('source', 'target')))

    files.update(
        await prepare_attachment_tsv(mongo_gridfs, response, ec_data, 'non_reflected_edges', header=('source', 'target')))

    return files


async def write_fc_data(response, scores_key, mongo_gridfs):
    files = {}

    scores = response[scores_key]
    fc_data = scores['fc_data']

    files.update(
        await prepare_attachment_tsv(mongo_gridfs, response, fc_data, 'fc_values_jaccard', header=('protein_1', 'protein_2', 'similarity')))

    files.update(
        await prepare_attachment_tsv(mongo_gridfs, response, fc_data, 'fc_values_hrss_bma', header=('protein_1', 'protein_2', 'similarity')))

    files.update(
        await prepare_attachment_tsv(mongo_gridfs, response, fc_data, 'unannotated_prots_net1', header=('unannotated proteins in net1',)))

    files.update(
        await prepare_attachment_tsv(mongo_gridfs, response, fc_data, 'unannotated_prots_net2', header=('unannotated proteins in net2',)))

    if 'ann_freqs_net1' in fc_data and 'ann_freqs_net2' in fc_data:
        files.update(write_ann_freqs(response, scores_key))

    return files


def write_ann_freqs(response, scores_key):
    files = {}

    scores = response[scores_key]
    fc_data = scores['fc_data']

    ann_freqs_net1 = [(int(ann_cnt), freq) for ann_cnt, freq in fc_data['ann_freqs_net1'].items()]
    total_prots_net1 = sum(freq for _, freq in ann_freqs_net1)
    rel_ann_freqs_net1 = [(ann_cnt, freq/total_prots_net1) for ann_cnt, freq in ann_freqs_net1]

    ann_freqs_net2 = [(int(ann_cnt), freq) for ann_cnt, freq in fc_data['ann_freqs_net2'].items()]
    total_prots_net2 = sum(freq for _, freq in ann_freqs_net2)
    rel_ann_freqs_net2 = [(ann_cnt, freq/total_prots_net2) for ann_cnt, freq in ann_freqs_net2]

    ann_freqs = [ann_freqs_net1, ann_freqs_net2]
    rel_ann_freqs = [rel_ann_freqs_net1, rel_ann_freqs_net2]

    for i in range(2):
        with NamedTemporaryFile(delete=False, mode='w', suffix='.tmp.tsv') as tmpfile:
            writer = csv_writer(tmpfile, delimiter='\t')
            writer.writerow(('number of GO annotations', 'number of proteins'))
            writer.writerows(ann_freqs[i])
            files[f'ann_freqs_net{i+1}.tsv'] = (tmpfile.name, False, ('text','csv'))

    for i in range(2):
        with NamedTemporaryFile(delete=False, mode='w', suffix='.tmp.tsv') as tmpfile:
            writer = csv_writer(tmpfile, delimiter='\t')
            writer.writerow(('number of GO annotations', 'proportion of proteins'))
            writer.writerows(rel_ann_freqs[i])
            files[f'rel_ann_freqs_net{i+1}.tsv'] = (tmpfile.name, False, ('text','csv'))

    with NamedTemporaryFile(delete=False, mode='w', suffix='.tmp.png') as tmpfile:
        fig = matplotlib_figure()
        axes = [[None, None], [None, None]]

        for i in range(2):
            ax = fig.add_subplot(2, 2, 1+i)
            axes[0][i] = ax
            ax.set_title(f'net{i+1}')
            ax.set_ylabel('Number of proteins')
            ax.set_xlabel('Number of GO annotations')
            li = ax.bar(*zip(*ann_freqs[i]))

        for i in range(2):
            if i == 0:
                ax = fig.add_subplot(2, 2, 3+i, sharex=axes[0][0])
            else:
                ax = fig.add_subplot(2, 2, 3+i, sharex=axes[0][1], sharey=axes[1][0])

            axes[1][i] = ax
            ax.set_title(f'net{i+1}')
            ax.set_ylabel('Proportion of proteins')
            ax.set_xlabel('Number of GO annotations')
            li = ax.bar(*zip(*rel_ann_freqs[i]))

        fig.tight_layout()
        fig.savefig(tmpfile.name)
        matplotlib_close(fig)
        files['ann_freq_hists.png'] = (tmpfile.name, True, ('image','png'))

    return files


async def write_scores_result_files(response, scores_key, mongo_gridfs):
    files = {}

    if scores_key in response:
        scores = response[scores_key]

        if 'ec_data' in scores:
            files.update(await write_ec_data(response, scores_key, mongo_gridfs))

        if 'fc_data' in scores:
            files.update(await write_fc_data(response, scores_key, mongo_gridfs))

    return files

async def write_alignment_result_files(response, mongo_gridfs):
    files = {}

    if 'results' not in response:
        return files

    results = response['results']

    if 'output' in results:
        output = results['output']

        with NamedTemporaryFile(delete=False, mode='w', suffix='.tmp.log') as tmpfile:
            tmpfile.write(output)
            files['output.log'] = (tmpfile.name, False, ('text', 'plain'))

    files.update(
        await prepare_attachment_tsv(mongo_gridfs, response, results, 'alignment'))

    files.update(
        await write_scores_result_files(response, 'scores', mongo_gridfs))

    return files


async def write_comparison_result_files(response, mongo_gridfs):
    files =  {}

    files.update(
        await write_scores_result_files(response, 'consensus_scores', mongo_gridfs))

    return files


async def send_email_alignment(response, emails, mongo_gridfs):
    await send_email(
        response,
        emails,
        subject = f"Alignment with {response['aligner']} finished",
        template_name = 'email-alignment-response.html.j2',
        files = await write_alignment_result_files(response, mongo_gridfs))

async def send_email_comparison(response, emails, mongo_gridfs):
    await send_email(
        response,
        emails,
        subject = "Alignment comparison finished",
        template_name = 'email-comparison-response.html.j2',
        files = await write_comparison_result_files(response, mongo_gridfs))


async def send_email(response, emails, subject, template_name, files=dict()):
    template = JINJA2_ENV.get_template(template_name)

    email_body = template.render(**response, base_url=BASE_URL)

    inline_files = []
    attachments = []

    for attachment_name, (tmp_file, inline, mime_type) in files.items():
        with open(tmp_file, 'rb') as fp:
            record = MIMEBase(*mime_type)
            record.set_payload(fp.read())
            encoders.encode_base64(record)
            if inline:
                record.add_header('Content-ID', '<' + attachment_name + '>')
                record.add_header('Content-Disposition', 'inline', filename=attachment_name)
                inline_files.append(record)
            else:
                record.add_header('Content-Disposition', 'attachment', filename=attachment_name)
                attachments.append(record)

        unlink(tmp_file)

    def _send_email(email):
        msg = MIMEMultipart('mixed')
        msg['Subject'] = subject
        msg['From'] = EMAIL_FROM
        msg['To'] = email

        body = MIMEMultipart('related')
        body.attach(MIMEText(email_body, 'html'))

        for inline_file in inline_files:
            body.attach(inline_file)

        msg.attach(body)

        for attachment in attachments:
            msg.attach(attachment)

        server.send_message(msg)

    server = SMTP('smtp.gmail.com', 587)
    server.ehlo()
    server.starttls()
    server.login(EMAIL_FROM, EMAIL_PASSWORD)
    list(map(_send_email, emails))
    server.quit()

    print(f"sent {subject}")
