#!/usr/bin/env python3
# Copyright (c) 2018, Palo Alto Networks
#
# Permission to use, copy, modify, and/or distribute this software for any
# purpose with or without fee is hereby granted, provided that the above
# copyright notice and this permission notice appear in all copies.
#
# THE SOFTWARE IS PROVIDED "AS IS" AND THE AUTHOR DISCLAIMS ALL WARRANTIES
# WITH REGARD TO THIS SOFTWARE INCLUDING ALL IMPLIED WARRANTIES OF
# MERCHANTABILITY AND FITNESS. IN NO EVENT SHALL THE AUTHOR BE LIABLE FOR
# ANY SPECIAL, DIRECT, INDIRECT, OR CONSEQUENTIAL DAMAGES OR ANY DAMAGES
# WHATSOEVER RESULTING FROM LOSS OF USE, DATA OR PROFITS, WHETHER IN AN
# ACTION OF CONTRACT, NEGLIGENCE OR OTHER TORTIOUS ACTION, ARISING OUT OF
# OR IN CONNECTION WITH THE USE OR PERFORMANCE OF THIS SOFTWARE.

# Authors: Edward Arcuri, Nathan Embery, Scott Shoaf

import click
import ast
from skilletlib import Panos
from skilletlib.exceptions import LoginException
from skilletlib.exceptions import SkilletLoaderException
from jinja2 import Environment, FileSystemLoader
from passlib.hash import md5_crypt

defined_filters = ['md5_hash']

class PythonLiteralOption(click.Option):

    def type_cast_value(self, ctx, value):
        try:
            return ast.literal_eval(value)
        except:
            raise click.BadParameter(value)

def md5_hash(txt):
    '''
    Returns the MD5 Hashed secret for use as a password hash in the PanOS configuration
    :param txt: text to be hashed
    :return: password hash of the string with salt and configuration information. Suitable to place in the phash field
    in the configurations
    '''
    return md5_crypt.hash(txt)

@click.command()
@click.option("-i", "--TARGET_IP", help="IP address of the device (localhost)", type=str, default="localhost")
@click.option("-r", "--TARGET_PORT", help="Port to communicate to NGFW (443)", type=int, default=443)
@click.option("-u", "--TARGET_USERNAME", help="Firewall Username (admin)", type=str, default="admin")
@click.option("-p", "--TARGET_PASSWORD", help="Firewall Password (admin)", type=str, default="admin")
@click.option("-s", "--infra_subnet", help="infrastructure subnet", type=str, default="192.168.254.0/24")
@click.option("-b", "--infra_bgp_as", help="infrastructure BGP AS", type=str, default="65534")
@click.option("-ph", "--portal_hostname", help="portal hostnamne", type=str, default="my-subdomain")
@click.option("-reg", "--deployment_region", help="deployment region", type=str, default="americas")
@click.option("-lam", "--deployment_locations_americas", help="deployment locations americas", cls=PythonLiteralOption, default="['us-east-1', 'us-west-1']")
@click.option("-leu", "--deployment_locations_europe", help="deployment locations europe", cls=PythonLiteralOption, default="['eu-west-1']")
@click.option("-lap", "--deployment_locations_apac", help="deployment locations apac", cls=PythonLiteralOption, default="['australia-east']")
@click.option("-pool", "--ip_pool_cidr", help="regional ip pool", type=str, default="192.168.2.0/23")
@click.option("-u1", "--user1_password", help="User1 password", type=str, default="Paloalto1")
@click.option("-u2", "--user2_password", help="User2 password", type=str, default="Paloalto2")
@click.option("-f", "--conf_filename", help="Configuration File Name", type=str, default="prisma_access_full_config.xml")

def cli(target_ip, target_port, target_username, target_password, infra_subnet, infra_bgp_as,
        portal_hostname, deployment_region, deployment_locations_americas, deployment_locations_europe,
        deployment_locations_apac, ip_pool_cidr, user1_password, user2_password, conf_filename):
    """
    Import a full configuration. Defaults values in parenthesis.
    """

    # creating the jinja context from the skillet vars
    context = dict()
    context['infra_subnet'] = infra_subnet
    context['infra_bgp_as'] = infra_bgp_as
    context['portal_hostname'] = portal_hostname
    context['deployment_region'] = deployment_region
    context['deployment_locations_americas'] = deployment_locations_americas
    context['deployment_locations_europe'] = deployment_locations_europe
    context['deployment_locations_apac'] = deployment_locations_apac
    context['ip_pool_cidr'] = ip_pool_cidr
    context['user1_password'] = user1_password
    context['user2_password'] = user2_password
    context['conf_filename'] = conf_filename

    # setup jinja environment and render template file
    env = Environment(loader=FileSystemLoader('templates'))
    env.filters['md5_hash'] = md5_hash
    template = env.get_template('prisma_access_full_config_vars.conf')
    file_contents = template.render(context)

    # create device option and use panoply import_file to send a config file to the device
    try:

        device = Panos(api_username=target_username,
                       api_password=target_password,
                       hostname=target_ip,
                       api_port=target_port
                       )

        if not device.import_file(conf_filename, file_contents, 'configuration'):
            exit(1)

        exit(0)

    except LoginException as lxe:
        print(lxe)
        exit(1)
    except SkilletLoaderException as pe:
        print(pe)
        exit(1)

    # failsafe
    exit(1)


if __name__ == '__main__':
    cli()