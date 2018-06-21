from logging import getLogger, Logger, basicConfig, DEBUG, WARNING
from typing import Sequence
import argparse

import add_captions_to_database


def main(args: Sequence[str] = None) -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument('input_dir', help='input files path')
    if args is None:
        params = parser.parse_args()
    else:
        params = parser.parse_args(args)

    logger = getLogger(__name__)
    entry = add_captions_to_database.AddCaptionsToDatabase(logger.getChild('AddCaptions'))
    entry.do(params.input_dir)


if __name__ == '__main__':
    main()
