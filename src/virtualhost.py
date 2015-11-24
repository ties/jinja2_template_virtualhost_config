import argparse
import os
import os.path

from jinja2 import FileSystemLoader, Environment

from pathtype import PathType

parser = argparse.ArgumentParser(
    epilog="This script does **not** perform any validation!")

parser.add_argument('type', type=str, choices=['nginx', 'apache'])

parser.add_argument('outputdir', type=PathType(exists=True, type='dir'),
                    help='Directory to write the config files to')

# Hostname (... important)
parser.add_argument('server_name', help='Hostname of the virtualhost')

# SSL certificate
parser.add_argument('--ssl_key', type=argparse.FileType('r'),
                    help='path of the ssl private key')

parser.add_argument('--ssl_chain', type=argparse.FileType('r'),
                    help='path of the certificate chain (all certs except for leaf)')
        
parser.add_argument('--ssl_cert', type=argparse.FileType('r'),
                    help='path of the ssl certificate, suitable for your server. This implies'
'that for nginx, this is the chain as sent to the client')

parser.add_argument('--dh_params', type=argparse.FileType('r'),
                    help='Diffie Hellman parameters (nginx)')
parser.add_argument('--log_dir', type=PathType(exists=True, type='dir'),
		    help='Directory for logs (for nginx)', default='/var/log/nginx')

# Standard apache settings
parser.add_argument('--server_admin', help='email-address of server-admin, '
                    'if available')
parser.add_argument('--document_root', type=PathType(exists=True, type='dir'),
                    help='document root')
parser.add_argument('--proxy_backend', help='url to reverse proxy to '
                    '(i.e. http://localhost:8080)')


args = parser.parse_args()

# Create jinja2 environment, render into outputdir
template_dir = os.path.join(
        os.path.dirname(os.path.abspath(__file__)),
        'templates', args.type)
env = Environment(loader=FileSystemLoader(template_dir))

http_template = env.get_template('http.conf')
https_template = env.get_template('https.conf')

# Translate file pointers into file names...
template_vars = vars(args)
for k, v in template_vars.items():
    if type(v) is file:
        template_vars[k] = v.name

http_config = os.path.join(args.outputdir,
                           'http_{}.conf'.format(args.server_name))
https_config = os.path.join(args.outputdir,
                            'https_{}.conf'.format(args.server_name))

with open(http_config, 'w') as f:
    f.write(http_template.render(**vars(args)))

with open(https_config, 'w') as f:
    f.write(https_template.render(**vars(args)))
