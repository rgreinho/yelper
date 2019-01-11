"""Define the top-level cli command."""
import logging
import os
import sys

import click
from loguru import logger

from yelper import config
from yelper.cli.base import AbstractCommand
from yelper.core.version import detect_from_metadata
from yelper.core.yelper import async_deep_query

# Set the project name.
APP_NAME = 'yelper'

# Retrieve the project version from packaging.
__version__ = detect_from_metadata(APP_NAME)


# pylint: disable=unused-argument
#   The arguments are used via the `self.args` dict of the `AbstractCommand` class.
@click.group()
@click.version_option(version=__version__)
@click.option('-v', '--verbose', count=True, help='defines the log level')
@click.pass_context
def cli(ctx, verbose):
    """Manage CLI commands."""
    ctx.obj = {**ctx.params}
    ctx.auto_envvar_prefix = 'VZ'

    # Load defaults from configuration file if any.
    cfg_path = os.path.join(click.get_app_dir(APP_NAME), APP_NAME + '.conf')
    cfg = cfg_path if os.path.exists(cfg_path) else None
    ctx.default_map = config.load(cfg, with_defaults=True, validate=True)

    # Configure logger.
    # The log level gets adjusted by adding/removing `-v` flags:
    #   None    : Initial log level is WARNING.
    #   -v      : INFO
    #   -vv     : DEBUG
    #   -vvv    : TRACE
    # For 2 `-v` and more, the log format also changes from compact to verbose.
    INITIAL_LOG_LEVEL = logging.WARNING
    LOG_FORMAT_COMPACT = "<level>{message}</level>"
    LOG_FORMAT_VERBOSE = "<level>{time:YYYY-MM-DDTHH:mm:ssZZ} {name}:{line:<4} {message}</level>"
    log_level = max(INITIAL_LOG_LEVEL - verbose * 10, 0)
    log_format = LOG_FORMAT_VERBOSE if log_level < logging.INFO else LOG_FORMAT_COMPACT

    # Remove any predefined logger.
    logger.remove()

    # Set the log colors.
    logger.level('ERROR', color='<red><bold>')
    logger.level('WARNING', color='<yellow>')
    logger.level('SUCCESS', color='<green>')
    logger.level('INFO', color='<cyan>')
    logger.level('DEBUG', color='<blue>')
    logger.level('TRACE', color='<magenta>')

    # Add the logger.
    logger.add(sys.stdout, format=log_format, level=log_level, colorize=True)


@click.command()
@click.option('--location', default='austin, tx', help='the geographic area to search', show_default=True)
@click.option('--offset', default=0, help='offset the list of results by this amount', show_default=True)
@click.option('--limit', default=25, help='maximum number of results per page', show_default=True)
@click.option('--radius', default=40000, help='search radius (in meters)', show_default=True)
@click.option('--output', default='yelper.csv', help='filename to store the results', show_default=True)
@click.option('--pages', default=0, help='number of result pages', show_default=True)
@click.argument('terms')
@click.pass_context
def retrieve(ctx, location, offset, limit, radius, output, pages, terms):
    """Retrieve information from Yelp."""
    command = Retrieve(ctx.params, ctx.obj)
    command.execute()


class Retrieve(AbstractCommand):
    """Retrieve information from Yelp."""

    def _execute(self):
        """Define the internal execution of the command."""
        async_deep_query(
            self.args['terms'],
            self.args['location'],
            self.args['offset'],
            self.args['limit'],
            self.args['radius'],
            self.args['output'],
            self.args['pages'],
        )


cli.add_command(retrieve)
