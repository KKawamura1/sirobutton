from django.core.management.base import BaseCommand
from logging import getLogger, Logger, basicConfig
import logging as logging_
from typing import Any
import argparse
import enum

import add_captions_to_database


class LogLevel(enum.Enum):
    debug = enum.auto()
    warning = enum.auto()

    def get_loglevel(self) -> Any:
        if self is LogLevel.debug:
            return logging_.DEBUG
        elif self is LogLevel.warning:
            return logging_.WARNING
        else:
            raise ValueError('no matching level!')


class Command(BaseCommand):
    help = 'Update database with the given caption data'

    def add_arguments(self, parser: argparse.ArgumentParser) -> None:
        parser.add_argument('input_dir', type=str)
        parser.add_argument('--log_level', choices=[level.name for level in LogLevel],
                            default=LogLevel.warning.name)

    def handle(self, *args: Any, **options: Any) -> None:
        input_dir: str = options['input_dir']
        log_level: LogLevel = LogLevel[options['log_level']]

        basicConfig(level=log_level.get_loglevel())
        logger = getLogger('__name__')
        entry = add_captions_to_database.AddCaptionsToDatabase(logger.getChild('AddCaptions'))
        entry.do(input_dir)
