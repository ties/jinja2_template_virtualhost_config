import argparse
import os
import os.path

from jinja2 import FileSystemLoader, Environment

from pathtype import PathType

parser = argparse.ArgumentParser(
    epilog="This script does **not** perform any validation!")

parser.add_argument('outputdir', type=PathType(exists=True, type='dir'),
                    help='Directory to write the config files to')

# Hostname (... important)
parser.add_argument('server_name', help='Hostname of the virtualhost')

# SSL certificate
parser.add_argument('--ssl_key', type=argparse.FileType('r'),
                    help='path of the ssl private key')

parser.add_argument('--ssl_chain', type=argparse.FileType('r'),
                    help='path of the certificate chain')
        
parser.add_argument('--ssl_cert', type=argparse.FileType('r'),
                    help='path of the ssl certificate')

# Standard apache settings
parser.add_argument('--server_admin', help='email-address of server-admin, '
                    'if available')
parser.add_argument('--document_root', type=PathType(exists=True, type='dir'),
                    help='document root')
parser.add_argument('--proxy_backend', help='url to reverse proxy to '
                    '(i.e. http://localhost:8080)')


args = parser.parse_args()

# Create jinja2 environment, render into outputdir
env = Environment(loader=FileSystemLoader('templates'))

template_env = dict(os.environ)
template_env['server_name'] = args.server_name

http_template = env.get_template('http.conf')
https_template = env.get_template('https.conf')

http_config = os.path.join(args.outputdir,
                           'http_{}.conf'.format(args.server_name))
https_config = os.path.join(args.outputdir,
                            'https_{}.conf'.format(args.server_name))

with open(http_config, 'w') as f:
    f.write(http_template.render(**template_env))

with open(https_config, 'w') as f:
    f.write(https_template.render(**template_env))
