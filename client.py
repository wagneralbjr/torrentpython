import string
import math
from typing import List, NamedTuple, Optional, Sequence, Dict

from typing import Any
from pprint import pprint
import bencoder
import random

import argparse

import hashlib
import requests

import logging

logging.basicConfig(level=logging.DEBUG)

logger = logging.getLogger()

PeersData = NamedTuple(
    "PeersData",
    [
        ("complete", int),
        ("incomplete", int),
        ("interval", int),
        ("peers", List[Dict[Any, Any]]),
    ],
)


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


def announce(torrent_data: Dict[Any, Any]) -> Any:
    # breakpoint()
    b_encoded_string = torrent_data[b"info"]

    info_hash = encode_info(b_encoded_string)

    random_peer_id = "".join(random.choices(string.ascii_lowercase, k=20))

    random_peer_id = hashlib.sha1(str(random_peer_id).encode("utf-8")).digest()

    uploaded = 0
    downloaded = 0
    # left = torrent_data[b"info"][b"pieces"]
    event = "started"
    total_length = math.ceil(
        int(torrent_data[b"info"][b"length"])
        / int(torrent_data[b"info"][b"piece length"])
    )

    url_announce = torrent_data[b"announce"].decode()

    print(url_announce)

    print(info_hash)
    print(random_peer_id)

    params = {
        "info_hash": info_hash,
        "peer_id": random_peer_id,
        "uploaded": uploaded,
        "port": 6881,
        "downloaded": downloaded,
        "left": total_length,
        "event": event,
    }

    print(params)

    logger.info("Announcing the torrent to download")
    r = requests.get(url_announce, params=params)

    logger.info(f"status_code={r.status_code}")

    peers_data = bencoder.decode(r.content)

    return peers_data


def parse_peers_data(p_data: Dict[Any, Any]) -> PeersData:
    data = PeersData(
        complete=p_data[b"complete"],
        incomplete=p_data[b"incomplete"],
        interval=p_data[b"interval"],
        peers=p_data[b"peers"],
    )
    return data


def buid_handshake(
    info_hash: Dict[Any, Any],
    peer_id: bytes,
    protocolstring: str = "BitTorrent",
):
    """handshake: <pstrlen><pstr><reserved><info_hash><peer_id>"""

    res = b""


def main(argv: Optional[Sequence[str]] = None) -> int:
    args = parse_args(argv)

    torrent_data = parse_torrent_file(args.file)
    # pprint(torrent_data)
    peers_data = announce(torrent_data)

    if "failure_reason" in peers_data:
        err_msg = f"There is a error in the announce metadata {peers_data}"
        raise ValueError(err_msg)

    print(peers_data)

    peers_data = parse_peers_data(peers_data)

    print(peers_data)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
