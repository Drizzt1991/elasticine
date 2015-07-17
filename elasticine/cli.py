# -*- coding: utf-8 -*-
from __future__ import print_function
import os
import os.path
import shutil
import yaml
from argparse import ArgumentParser

try:
    import jinja2
except ImportError:
    jinja2 = None

from . import utils

# FIXME: Load from `templates` folder by os.listdir maybe...
TEMPLATES = ['generic']
TEMPLATE_FOLDER = os.path.join(os.path.dirname(__file__), "templates")


def setup_parsers():
    main_parser = ArgumentParser(
        description="Elastic migration tool")
    main_parser.add_argument(
        "-c", "--config", help="Path to config file",
        default="./elasticine.yaml")

    subparsers = main_parser.add_subparsers(
        metavar="COMMAND", help="Select one of following commands:")

    # ``history`` command
    history = subparsers.add_parser(
        'history',
        help='Show migration history and current revision of Elastic cluster')
    history.set_defaults(command=HistoryCommand())

    # ``current`` command
    subparsers.add_parser(
        'current',
        help='Show current revision of Elastic cluster')

    # ``upgrade`` command
    upgrade = subparsers.add_parser(
        'upgrade',
        help='Perform data migration on Elastic cluster')
    upgrade.add_argument(
        "revision",
        help="Revision to upgrade to. You can also specify an `int` for number"
             " of revisions to upgrade")
    upgrade.set_defaults(command=UpgradeCommand())

    # ``revision`` command
    subparsers.add_parser(
        'revision',
        help='Create a new revision file in `revisions` folder')

    # ``init`` command
    init = subparsers.add_parser(
        'init',
        help='Create a new elasticine migration folders layout')
    init.add_argument(
        "directory",
        help="Path to directory where to set-up the folder layout")
    init.add_argument(
        "-t", "--template", choices=TEMPLATES,
        metavar="TEMPLATE", default="generic",
        help="Name of template to use. Select one of: " +
             ", ".join(TEMPLATES))
    init.set_defaults(command=InitCommand())

    return main_parser


def main():
    parser = setup_parsers()
    args = parser.parse_args()
    # Execute subcommand set by `set_defaults` of subparser
    if hasattr(args, 'command'):
        try:
            args.command(args)
        except CommandError as exc:
            print('error: {}'.format(exc))


class CommandError(Exception):
    """ Simple exc used to pass message out of command class and format it
        in a similar mannar
    """


class Command(object):
    """ Base class is mainly to have similar code encapsulated as methods
    """

    def __init__(self):
        pass

    def __call__(self, args):
        raise NotImplementedError

    def validate_config(self, args, config):
        if 'elasticine' not in config:
            raise CommandError(
                "Bad config file: could not find `elasticine` section")
        if 'elastic' not in config['elasticine']:
            raise CommandError(
                "Bad config file: did not find adapter config at"
                " `elasticine.elastic`")

        revisions_folder = config["elasticine"].get("revisions_folder")
        if revisions_folder is None:
            revisions_folder = "./"
        # We will lookup path's from config file location if relative
        if not os.path.isabs(revisions_folder):
            base = os.path.dirname(args.config)
            revisions_folder = os.path.join(base, revisions_folder)
        config['elasticine']['revisions_folder'] = revisions_folder

        return config

    def load_config(self, args):
        if os.path.exists(args.config):
            with open(args.config) as f:
                return self.validate_config(args, yaml.load(f))
        else:
            raise CommandError(
                "Config at {} does not exist".format(args.config))

    def status(self, msg):
        print(' '*2 + msg)

    def msg(self, msg):
        print(msg)


class HistoryCommand(Command):

    def __call__(self, args):
        pass


class UpgradeCommand(Command):

    def __call__(self, args):
        config = self.load_config(args)

        environment = utils.import_file_as_py(
            os.path.join(config['elasticine']['revisions_folder'], 'env.py'))

        migrator = environment.configure(config)


class InitCommand(Command):

    def __call__(self, args):
        directory = args.directory
        if os.access(directory, os.F_OK):
            raise CommandError("Directory `{}` already exists".format(
                directory))
        template = args.template
        template_path = os.path.join(TEMPLATE_FOLDER, template)
        if not os.access(template_path, os.F_OK):
            raise CommandError("No such template `{}`".format(
                template))

        self.status("mkdir `{}`".format(directory))
        os.mkdir(directory)

        # Copy files, optionaly formatting them with jinja2
        for filename in os.listdir(template_path):
            file_src = os.path.join(template_path, filename)
            file_dst = os.path.join(directory, filename)
            if os.path.isdir(file_src):
                self.status("mkdir `{}`".format(filename))
                os.mkdir(file_dst)
            else:
                self.status("copy `{}`".format(filename))
                shutil.copy(file_src, file_dst)

        self.msg("Please edit config at {} before proceeding".format(
            os.path.join(directory, 'elasticine.yaml')))
