"""
Copyright (C) 2022  kyomi

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <https://www.gnu.org/licenses/>.
"""

import os
import contextlib
import logging
from logging.handlers import RotatingFileHandler

import click
import humanize

from bot.core import UnBot


__all__ = ()


@contextlib.contextmanager
def setup_logging():
    log = logging.getLogger()

    try:
        # __enter__
        max_bytes = 32 * 1024 * 1024 # 32 MiB

        logging.getLogger("discord").setLevel(logging.INFO)
        logging.getLogger("discord.http").setLevel(logging.WARN)

        datetime_format = r'%Y-%m-%d %H:%M:%S'
        log_format = "[{asctime}] [{levelname}] {name}: {message}"
        log.setLevel(logging.INFO)

        file_handler = RotatingFileHandler(
            filename="unbot.log",
            encoding="utf-8",
            maxBytes=max_bytes,
            backupCount=5,
        )
        formatter = logging.Formatter(log_format, datetime_format, style="{")

        file_handler.setFormatter(formatter)
        log.addHandler(file_handler)

        yield
    finally:
        # __exit__
        for handler in log.handlers:
            handler.close()
            log.removeHandler(handler)


def run_bot():
    humanize.activate("pt_BR")

    bot = UnBot()
    token = os.environ["TOKEN"]
    
    bot.run(token)


@click.group(invoke_without_command=True, options_metavar="[options]")
@click.pass_context
def main(ctx: click.Context):
    """
    Launches the bot.
    """
    if not ctx.invoked_subcommand:
        with setup_logging():
            run_bot()


if __name__ == "__main__":
    main()
