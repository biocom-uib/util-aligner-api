from smtplib import SMTP
from email import encoders
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from bson.objectid import ObjectId
from csv import writer as csv_writer
from os import unlink
from tempfile import NamedTemporaryFile
from config import config

from jinja2 import Environment, FileSystemLoader, select_autoescape

from matplotlib import use as matplotlib_use
matplotlib_use('Agg')
from matplotlib.pyplot import figure as matplotlib_figure
from seaborn import set as seaborn_set
seaborn_set()

EMAIL_FROM = config['EMAIL_FROM']
EMAIL_PASSWORD = config['EMAIL_PASSWORD']

JINJA2_ENV = Environment(
    loader = FileSystemLoader('/opt/templates'),
    autoescape = select_autoescape(['html', 'xml'])
)


async def write_result_files(response, mongo_gridfs):
    files = {}

    if 'results' not in response:
        return files

    results = response['results']

    if 'output' in results:
        output = results['output']

        with NamedTemporaryFile(delete=False, mode='w', suffix='.tmp.log') as tmpfile:
            tmpfile.write(output)
            files['output.log'] = (tmpfile.name, False, ('text','plain'))

    if 'alignment' in results:
        alignment = results['alignment']

        if alignment is None:
            with NamedTemporaryFile(delete=False, mode='wb', suffix='.tmp.tsv') as tmpfile:
                await mongo_gridfs.download_to_stream(ObjectId(response['files']['alignment_tsv']), tmpfile)
        else:
            with NamedTemporaryFile(delete=False, mode='w', suffix='.tmp.tsv') as tmpfile:
                writer = csv_writer(tmpfile, delimiter='\t')
                writer.writerow(alignment_header)
                writer.writerows(alignment)
                files['alignment.tsv'] = (tmpfile.name, False, ('text','csv'))

    if 'scores' in response:
        scores = response['scores']

        if 'ec_data' in scores:
            files.update(await write_ec_data(response, mongo_gridfs))

        if 'fc_data' in scores:
            files.update(await write_fc_data(response, mongo_gridfs))

    return files

async def write_ec_data(response, mongo_gridfs):
    files = {}

    scores = response['scores']
    ec_data = scores['ec_data']

    if 'non_preserved_edges' in ec_data:
        non_preserved_edges = ec_data['non_preserved_edges']

        if non_preserved_edges is None:
            with NamedTemporaryFile(delete=False, mode='wb', suffix='.tmp.tsv') as tmpfile:
                await mongo_gridfs.download_to_stream(ObjectId(response['files']['non_preserved_edges_tsv']), tmpfile)
        else:
            with NamedTemporaryFile(delete=False, mode='w', suffix='.tmp.tsv') as tmpfile:
                writer = csv_writer(tmpfile, delimiter='\t')
                writer.writerow(('source','target'))
                writer.writerows((row,) for row in non_preserved_edges)
                files['non_preserved_edges.tsv'] = (tmpfile.name, False, ('text','csv'))

    if 'non_reflected_edges' in ec_data:
        non_reflected_edges = ec_data['non_reflected_edges']

        if non_reflected_edges is None:
            with NamedTemporaryFile(delete=False, mode='wb', suffix='.tmp.tsv') as tmpfile:
                await mongo_gridfs.download_to_stream(ObjectId(response['files']['non_reflected_edges_tsv']), tmpfile)
        else:
            with NamedTemporaryFile(delete=False, mode='w', suffix='.tmp.tsv') as tmpfile:
                writer = csv_writer(tmpfile, delimiter='\t')
                writer.writerow(('source','target'))
                writer.writerows((row,) for row in non_reflected_edges)
                files['non_reflected_edges.tsv'] = (tmpfile.name, False, ('text','csv'))

    return files

async def write_fc_data(response, mongo_gridfs):
    files = {}

    scores = response['scores']
    fc_data = scores['fc_data']

    if 'fc_values_jaccard' in fc_data:
        fc_values_jaccard = fc_data['fc_values_jaccard']

        with NamedTemporaryFile(delete=False, mode='w', suffix='.tmp.tsv') as tmpfile:
            writer = csv_writer(tmpfile, delimiter='\t')
            writer.writerow(('protein 1', 'protein 2', 'similarity'))
            writer.writerows(fc_values_jaccard)
            files['fc_values_jaccard.tsv'] = (tmpfile.name, False, ('text','csv'))

    if 'fc_values_hrss' in fc_data:
        fc_values_hrss = fc_data['fc_values_hrss']

        with NamedTemporaryFile(delete=False, mode='w', suffix='.tmp.tsv') as tmpfile:
            writer = csv_writer(tmpfile, delimiter='\t')
            writer.writerow(('protein 1', 'protein 2', 'similarity'))
            writer.writerows(fc_values_hrss)
            files['fc_values_hrss.tsv'] = (tmpfile.name, False, ('text','csv'))

    if 'unannotated_prots_net1' in fc_data:
        unannotated_prots_net1 = fc_data['unannotated_prots_net1']

        with NamedTemporaryFile(delete=False, mode='w', suffix='.tmp.tsv') as tmpfile:
            writer = csv_writer(tmpfile, delimiter='\t')
            writer.writerow(('unannotated proteins in net1',))
            writer.writerows((row,) for row in unannotated_prots_net1)
            files['unannotated_prots_net1.tsv'] = (tmpfile.name, False, ('text','csv'))

    if 'unannotated_prots_net2' in fc_data:
        unannotated_prots_net2 = fc_data['unannotated_prots_net2']

        with NamedTemporaryFile(delete=False, mode='w', suffix='.tmp.tsv') as tmpfile:
            writer = csv_writer(tmpfile, delimiter='\t')
            writer.writerow(('unannotated proteins in net2',))
            writer.writerows((row,) for row in unannotated_prots_net2)
            files['unannotated_prots_net2.tsv'] = (tmpfile.name, False, ('text','csv'))

    if 'ann_freqs_net1' in fc_data and 'ann_freqs_net2' in fc_data:
        files.update(write_ann_freqs(response))

    return files

def write_ann_freqs(response):
    files = {}

    scores = response['scores']
    fc_data = scores['fc_data']

    ann_freqs_net1 = [(int(ann_cnt), freq) for ann_cnt, freq in fc_data['ann_freqs_net1'].items()]
    total_prots_net1 = sum(freq for _, freq in ann_freqs_net1)
    rel_ann_freqs_net1 = [(ann_cnt, freq/total_prots_net1) for ann_cnt, freq in ann_freqs_net1]

    ann_freqs_net2 = [(int(ann_cnt), freq) for ann_cnt, freq in fc_data['ann_freqs_net2'].items()]
    total_prots_net2 = sum(freq for _, freq in ann_freqs_net2)
    rel_ann_freqs_net2 = [(ann_cnt, freq/total_prots_net2) for ann_cnt, freq in ann_freqs_net2]

    ann_freqs = [[ann_freqs_net1, ann_freqs_net2], [rel_ann_freqs_net1, rel_ann_freqs_net2]]

    for i in range(2):
        with NamedTemporaryFile(delete=False, mode='w', suffix='.tmp.tsv') as tmpfile:
            writer = csv_writer(tmpfile, delimiter='\t')
            writer.writerow(('number of GO annotations', 'number of proteins'))
            writer.writerows(ann_freqs[0][i])
            files[f'ann_freqs_net{i+1}.tsv'] = (tmpfile.name, False, ('text','csv'))

    for i in range(2):
        with NamedTemporaryFile(delete=False, mode='w', suffix='.tmp.tsv') as tmpfile:
            writer = csv_writer(tmpfile, delimiter='\t')
            writer.writerow(('number of GO annotations', 'proportion of proteins'))
            writer.writerows(ann_freqs[1][i])
            files[f'rel_ann_freqs_net{i+1}.tsv'] = (tmpfile.name, False, ('text','csv'))

    with NamedTemporaryFile(delete=False, mode='w', suffix='.tmp.png') as tmpfile:
        fig = matplotlib_figure()
        axes = [[None, None], [None,None]]

        for i in range(2):
            ax = fig.add_subplot(2, 2, 1+i)
            axes[0][i] = ax
            ax.set_title(f'net{i+1}')
            ax.set_ylabel('Number of proteins')
            ax.set_xlabel('Number of GO annotations')
            li = ax.bar(*zip(*ann_freqs[0][i]))

        for i in range(2):
            if i == 0:
                ax = fig.add_subplot(2, 2, 3+i, sharex=axes[0][0])
            else:
                ax = fig.add_subplot(2, 2, 3+i, sharex=axes[0][1], sharey=axes[1][0])

            axes[1][i] = ax
            ax.set_title(f'net{i+1}')
            ax.set_ylabel('Proportion of proteins')
            ax.set_xlabel('Number of GO annotations')
            li = ax.bar(*zip(*ann_freqs[1][i]))

        fig.tight_layout()
        fig.savefig(tmpfile.name)
        files['ann_freq_hists.png'] = (tmpfile.name, True, ('image','png'))

    return files


async def send_email(response, emails, mongo_gridfs):
    template = JINJA2_ENV.get_template('email-response.html.j2')

    print('rendering template')
    email_body = template.render(**response)

    tmp_files = await write_result_files(response, mongo_gridfs)
    inline_files = []
    attachments = []

    for attachment_name, (tmp_file, inline, mime_type) in tmp_files.items():
        print(f'processing attachment {attachment_name}')

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
        msg['Subject'] = 'Alignment Finished'
        msg['From'] = EMAIL_FROM
        msg['To'] = email
        msg.preamble = 'Results for alignment'

        body = MIMEMultipart('related')
        body.attach(MIMEText(email_body, 'html'))

        for inline_file in inline_files:
            body.attach(inline_file)

        msg.attach(body)

        for attachment in attachments:
            msg.attach(attachment)

        server.send_message(msg)

    print('sending')

    server = SMTP('smtp.gmail.com', 587)
    server.ehlo()
    server.starttls()
    server.login(EMAIL_FROM, EMAIL_PASSWORD)
    list(map(_send_email, emails))
    server.quit()
