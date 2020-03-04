"""Console script for openapi_to_markdown."""
import argparse
import logging
import os
import sys

from . import openapi_to_markdown

logger = logging.getLogger(__name__)


def main():
    """Console script for openapi_to_markdown."""
    parser = argparse.ArgumentParser()
    parser.add_argument('--log-level', default=os.getenv('LOGGING_LEVEL', 'INFO'))
    parser.add_argument('--log-config', default=os.getenv('LOGGING_CONFIG', 'logging.yaml'))
    parser.add_argument('filename', type=str, help='')
    args = parser.parse_args()

    logging.basicConfig(level=args.log_level)

    parser = openapi_to_markdown.ResolvingParser(args.filename)
    endpoints = openapi_to_markdown.retrieve_endpoint(parser.specification)
    summary = openapi_to_markdown.get_summary_info(endpoints)
    print(summary)
    detail = openapi_to_markdown.get_detail_info(endpoints)
    print(detail)


if __name__ == "__main__":
    sys.exit(main())  # pragma: no cover
