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


def build_random_peer_id() -> bytes:
    random_peer_id = "".join(random.choices(string.ascii_lowercase, k=20))
    random_peer_id = hashlib.sha1(str(random_peer_id).encode("utf-8")).digest()
    return random_peer_id


def announce(
    torrent_data: Dict[Any, Any], info_hash: bytes, random_peer_id: bytes
) -> Any:
    # breakpoint()
    b_encoded_string = torrent_data[b"info"]

    # info_hash = encode_info(b_encoded_string)

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


def build_handshake(info_hash: bytes, peer_id: bytes, protocol_string):
    """handshake: <pstrlen><pstr><reserved><info_hash><peer_id>"""

    handshake = str(len(protocol_string)).encode()
    handshake += protocol_string.encode()
    reserved = b"00000000"
    handshake += reserved
    handshake += info_hash
    handshake += peer_id

    print(type(handshake))
    print(handshake)

    return handshake


def build_info_hash(torrent_data: Dict[Any, Any]) -> bytes:
    b_encoded_string = torrent_data[b"info"]
    info_hash = encode_info(b_encoded_string)

    return info_hash


def main(argv: Optional[Sequence[str]] = None) -> int:
    args = parse_args(argv)

    protocol_string = "BitTorrent protocol"
    torrent_data = parse_torrent_file(args.file)
    random_peer_id = build_random_peer_id()
    info_hash = build_info_hash(torrent_data)
    peers_data = announce(torrent_data, info_hash, random_peer_id)

    if "failure_reason" in peers_data:
        err_msg = f"There is a error in the announce metadata {peers_data}"
        raise ValueError(err_msg)

    print(peers_data)

    peers_data = parse_peers_data(peers_data)
    print(peers_data)
    handshake = build_handshake(info_hash, random_peer_id, protocol_string)

    print(handshake)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
