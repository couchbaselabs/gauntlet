import click
import functools
import yaml


def read_config_yaml(config_file_path):
    with open(config_file_path, "r") as fp:
        config_data = yaml.load(fp.read(), Loader=yaml.FullLoader)
    return config_data["e2e_app"]


def auth_options(f):
    options = [
        click.option("--password", '-p', default=None, help="Password"),
        click.option("--username", '-u', default=None, help="Username"),
    ]
    return functools.reduce(lambda x, opt: opt(x), options, f)


def common_options(f):
    options = [
        click.option("--config", default="config.yaml",
                     help="Config for the interface")
    ]
    return functools.reduce(lambda x, opt: opt(x), options, f)
