import string
from typing import Optional, Sequence, Dict

from typing import Any
from pprint import pprint
import bencoder
import random

import argparse

import hashlib
import requests

import logging

logging.basicConfig(level=logging.DEBUG)


def parse_args(argv: Optional[Sequence[str]] = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--file", type=str, required=True)

    args = parser.parse_args(argv)

    return args


def parse_torrent_file(filename: str) -> Any:
    with open(filename, "rb") as file:
        data = bencoder.decode(file.read())

    return data


def encode_info(info: bytes) -> bytes:
    hash = hashlib.sha1(bencoder.encode(info)).digest()

    return hash


def announce(torrent_data: Dict[Any, Any]) -> Dict:
    # breakpoint()
    b_encoded_string = torrent_data[b"info"]

    info_hash = encode_info(b_encoded_string)

    random_peer_id = "".join(random.choices(string.ascii_lowercase, k=20))

    uploaded = 0
    downloaded = 0
    left = len(torrent_data[b"info"][b"pieces"])
    event = "started"

    url_announce = torrent_data[b"announce"].decode()

    print(url_announce)

    print(info_hash)
    print(random_peer_id)

    params = {
        "info_hash": info_hash,
        "peer_id": random_peer_id,
        "uploaded": str(uploaded),
        "downloaded": str(downloaded),
        "left": str(left),
        "event": event,
    }

    print(params)
    r = requests.get(url_announce, params=params)

    print(r, r.text)


def main(argv: Optional[Sequence[str]] = None) -> int:
    args = parse_args(argv)

    torrent_data = parse_torrent_file(args.file)

    # pprint(torrent_data)

    announce(torrent_data)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
