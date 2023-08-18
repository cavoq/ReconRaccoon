#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import argparse
from src.framework import cli
# Custom imports
import re
import os
import urllib3
import requests
from concurrent.futures import ThreadPoolExecutor, as_completed

# Disable Warnings
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
requests.adapters.DEFAULT_RETRIES = 100


# Crawl
def crawl(target, timeout, headers, verbose, regex):
    sesh = requests.session()
    sesh.keep_alive = False
    try:
        r = sesh.get(target, allow_redirects=False, verify=False, timeout=timeout, headers=headers)
        body = r.content.decode('utf-8')
        match = re.findall(regex, body, re.I)
        if r.status_code in range(100, 199):
            print(f'{cli.blue}INFO{cli.endc} - {target} [{cli.blue}{r.status_code}{cli.endc}]')
        elif r.status_code in range(200, 299):
            print(f'{cli.green}SUCCESS{cli.endc} - {target} [{cli.green}{r.status_code}{cli.endc}]')
        elif r.status_code in range(300, 399):
            print(
                f'{cli.yellow}REDIRECTION{cli.endc} - {target} [{cli.yellow}{r.status_code}{cli.endc}] {cli.yellow}→{cli.endc} {r.headers["location"]}')
        elif r.status_code in range(400, 499):
            print(f'{cli.purple}CLIENT_ERROR{cli.endc} - {target} [{cli.purple}{r.status_code}{cli.endc}]')
        elif r.status_code in range(500, 599):
            print(f'{cli.red}SERVER_ERROR{cli.endc} - {target} [{cli.red}{r.status_code}{cli.endc}]')
        else:
            pass
        for x in match:
            print(f'├─[{x}]')
        print(f'└─ Fetched {cli.bold}{len(match)}{cli.endc} paths...')
    except requests.exceptions.ConnectTimeout:
        if verbose is True:
            print(f'{cli.red}TIMEOUT{cli.endc} - {target} [{cli.red}after {timeout}/s {cli.endc}]')
        return None
    except Exception as E:
        if verbose is True:
            print(f'{cli.red}ERROR{cli.endc} - {target} [{cli.red}{E}{cli.endc}]')
        return None


# Init
def __init__():
    parser = argparse.ArgumentParser(prog='ReconRacoon.py crawl', description='Crawl Module')
    parser.add_argument('-t', '--target', dest='target', type=str, required=True, help='Target URLs or IPs (str/file)')
    parser.add_argument('-c', '--custom-regex', dest='regex', type=str, default=r'''(?:href|src|action)=([^\s]*[\"|'])''', help=r'''Crawl request body for custom regex  (default="(?:href|src|action)=([^\s]*[\"|'])")''')
    parser.add_argument('-r', '--request-timeout', dest='timeout', type=float, default=1.0, help='Timeout for all http requests (default=1.0)')
    parser.add_argument('-a', '--active-threads', dest='threads', type=int, default=20, help='Threads for all http requests (default=20)')
    parser.add_argument('-u', '--user-agent', dest='user_agent', default='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36', type=str, help='Use custom user agent')
    parser.add_argument('-v', '--verbose', action='store_true', help='Display verbose output (timeouts/errors)')
    args, sysargs = parser.parse_known_args()
    # Call main function
    main(args)


# Main
def main(args):
    print(f'{cli.blue}[*]{cli.endc} Regex: {args.regex}')
    # Validate Target
    if os.path.isfile(args.target) is True:
        with open(args.target) as file:
            target = [x.strip() for x in file.readlines()]
    else:
        target = str(args.target)
    try:
        if type(target) is list:
            threads = []
            with ThreadPoolExecutor(max_workers=args.threads) as executor:
                for url in target:
                    threads.append(executor.submit(crawl, target=f'http://{url}', timeout=args.timeout, headers={'User-Agent': args.user_agent}, verbose=args.verbose, regex=args.regex))
                    threads.append(executor.submit(crawl, target=f'https://{url}', timeout=args.timeout, headers={'User-Agent': args.user_agent}, verbose=args.verbose, regex=args.regex))
        if type(target) is str:
            threads = []
            with ThreadPoolExecutor(max_workers=args.threads) as executor:
                threads.append(executor.submit(crawl, target=f'http://{target}', timeout=args.timeout, headers={'User-Agent': args.user_agent}, verbose=args.verbose, regex=args.regex))
                threads.append(executor.submit(crawl, target=f'https://{target}', timeout=args.timeout, headers={'User-Agent': args.user_agent}, verbose=args.verbose, regex=args.regex))
    except KeyboardInterrupt:
        print(f'{cli.red} leaving..{cli.endc}')
        exit()
