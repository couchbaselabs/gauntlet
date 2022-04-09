import click

from constants.app import E2EApp
from commands.flight import flight
from commands.profile import profile
from lib.common import auth_options, common_options


@click.group()
@auth_options
@common_options
def e2e_interface(config, username, password):
    E2EApp.CONFIG_YAML = config
    E2EApp.USERNAME = username
    E2EApp.PASSWORD = password


if __name__ == "__main__":
    for cmd in [flight, profile]:
        e2e_interface.add_command(cmd)
    e2e_interface()
