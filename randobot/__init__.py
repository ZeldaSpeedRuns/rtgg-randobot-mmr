import argparse
import logging
import os
import sys

from dotenv import load_dotenv

from .bot import RandoBot


def main():
    # Load environment variables from .env file
    load_dotenv()

    parser = argparse.ArgumentParser(
        description='RandoBot, because MMR seeds weren\'t scary enough already.',
    )
    parser.add_argument('--mmr-api-key', type=str, help='mmrandomizer.com API key (default: MMR_API_KEY env var)')
    parser.add_argument('--category-slug', type=str, help='racetime.gg category (default: CATEGORY_SLUG env var)')
    parser.add_argument('--client-id', type=str, help='racetime.gg client ID (default: CLIENT_ID env var)')
    parser.add_argument('--client-secret', type=str, help='racetime.gg client secret (default: CLIENT_SECRET env var)')
    parser.add_argument('--verbose', '-v', action='store_true', help='verbose output')
    parser.add_argument('--host', type=str, nargs='?', help='change the ractime.gg host (debug only!')
    parser.add_argument('--insecure', action='store_true', help='don\'t use HTTPS (debug only!)')

    args = parser.parse_args()

    # Get config from CLI args or environment variables
    mmr_api_key = args.mmr_api_key or os.getenv('MMR_API_KEY')
    category_slug = args.category_slug or os.getenv('CATEGORY_SLUG')
    client_id = args.client_id or os.getenv('CLIENT_ID')
    client_secret = args.client_secret or os.getenv('CLIENT_SECRET')

    # Validate required config
    if not mmr_api_key:
        parser.error('mmr_api_key is required (via --mmr-api-key or MMR_API_KEY env var)')
    if not category_slug:
        parser.error('category_slug is required (via --category-slug or CATEGORY_SLUG env var)')
    if not client_id:
        parser.error('client_id is required (via --client-id or CLIENT_ID env var)')
    if not client_secret:
        parser.error('client_secret is required (via --client-secret or CLIENT_SECRET env var)')

    logger = logging.getLogger()
    handler = logging.StreamHandler(sys.stdout)

    if args.verbose:
        logger.setLevel(logging.DEBUG)
        handler.setLevel(logging.DEBUG)

    handler.setFormatter(logging.Formatter(
        '[%(asctime)s] %(name)s (%(levelname)s) :: %(message)s'
    ))
    logger.addHandler(handler)

    if args.host:
        RandoBot.racetime_host = args.host
    if args.insecure:
        RandoBot.racetime_secure = False

    inst = RandoBot(
        mmr_api_key=mmr_api_key,
        category_slug=category_slug,
        client_id=client_id,
        client_secret=client_secret,
        logger=logger,
    )
    inst.run()


if __name__ == '__main__':
    main()
