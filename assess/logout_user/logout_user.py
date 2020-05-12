import base64

import click
from skilletlib import Panos
from skilletlib.exceptions import LoginException
from skilletlib.exceptions import SkilletLoaderException


@click.command()
@click.option("-i", "--TARGET_IP", help="IP address of the device (localhost)", type=str, default="localhost")
@click.option("-r", "--TARGET_PORT", help="Port to communicate to NGFW (443)", type=int, default=443)
@click.option("-u", "--TARGET_USERNAME", help="Firewall Username (admin)", type=str, default="admin")
@click.option("-p", "--TARGET_PASSWORD", help="Firewall Password (admin)", type=str, default="admin")
@click.option("-m", "--mobile_user", help="Mobile Username", type=str, default="test@test.com")
def cli(target_ip, target_port, target_username, target_password, mobile_user):
    """
    logout mobile user
    """

    username_bytes = mobile_user.encode('ascii')
    base64_bytes = base64.b64encode(username_bytes)
    base64_username = base64_bytes.decode('ascii')

    print(f'encoded mobile username is: {base64_username}')

    try:

        device = Panos(api_username=target_username,
                       api_password=target_password,
                       hostname=target_ip,
                       api_port=target_port

                       )
        params = {}
        params['cmd'] = 'op'
        params['cmd_str'] = \
            f'<request><plugins><cloud_services><gpcs><logout_mobile_user><gateway><computer>*</computer>' \
            f'<user>{base64_username}=</user></gateway></logout_mobile_user></gpcs></cloud_services></plugins></request>'

        if not device.execute_cmd(params):
            exit(1)

        print(device.xapi.xml_result())
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
