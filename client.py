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
import socket
from enum import Enum
import struct


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


class MessageType(Enum):
    MSG_CHOCKE = 0
    MSG_UNCHOCKE = 1
    MSG_INTERESTED = 2
    MSG_NOT_INTERESTED = 3
    MSG_HAVE = 4
    MSG_BITFIELD = 5
    MSG_REQUEST = 6
    MSG_PIECE = 7
    MSG_CANCEL = 8


Message = NamedTuple(
    "Message",
    [
        ("id", MessageType),
        ("payload", bytes),
    ],
)


def parse_args(argv: Optional[Sequence[str]] = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--file", type=str, required=True)
    parser.add_argument("--debug", type=bool, required=False, default=False)

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
    uploaded = 0
    downloaded = 0
    event = "started"
    total_length = math.ceil(
        int(torrent_data[b"info"][b"length"])
        / int(torrent_data[b"info"][b"piece length"])
    )

    url_announce = torrent_data[b"announce"].decode()

    params = {
        "info_hash": info_hash,
        "peer_id": random_peer_id,
        "uploaded": uploaded,
        "port": 6881,
        "downloaded": downloaded,
        "left": total_length,
        "event": event,
    }

    logger.info("Announcing the torrent to download")
    logging.info(f"params={params}")
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


def build_handshake(info_hash: bytes, peer_id: bytes, protocol_string: str):
    """handshake: <pstrlen><pstr><reserved><info_hash><peer_id>"""

    if len(info_hash) != 20:
        raise ValueError("Wrong number of byutes with info_hash")

    reserved = b"\x00" * 8
    handshake = struct.pack(
        ">B{}s8s20s20s".format(len(protocol_string)),
        len(protocol_string),
        protocol_string.encode(),
        reserved,
        info_hash,
        peer_id,
    )

    print(handshake)

    return handshake


def build_info_hash(torrent_data: Dict[Any, Any]) -> bytes:
    b_encoded_string = torrent_data[b"info"]
    info_hash = encode_info(b_encoded_string)

    return info_hash


class IPVERSION(Enum):
    IPV4 = socket.AF_INET
    IPV6 = socket.AF_INET6


def check_ip_protocol_version(possible_ip: bytes) -> Any:
    """find the .encode()type of connection"""
    possible_ip = possible_ip.decode("utf-8")  # type: ignore

    if ":" not in str(possible_ip):
        return IPVERSION.IPV4
    else:
        return IPVERSION.IPV6


def fetch_pieces(peers_data: PeersData, handshake: bytes):
    for peer in peers_data.peers:
        IP_CONN_TYPE = check_ip_protocol_version(peer[b"ip"])

        HOST = peer[b"ip"].decode("utf-8")
        PORT = peer[b"port"]

        if IP_CONN_TYPE == IPVERSION.IPV4:
            CONN_TUPLE = (HOST, PORT)
            SOCKET_TYPE = socket.AF_INET
        else:
            CONN_TUPLE = (HOST, PORT, 0, 0)
            SOCKET_TYPE = socket.AF_INET6

        print(IP_CONN_TYPE)
        print(CONN_TUPLE)
        with socket.socket(
            SOCKET_TYPE,  # type: ignore
            socket.SOCK_STREAM,
        ) as s:
            try:
                s.settimeout(5)
                s.connect(CONN_TUPLE)
                s.sendall(handshake)

                print("Dados recebidos")
                data = s.recv(1)
                print(data)
                if data != b"\x13":
                    logging.info(f"Could not handshake with {CONN_TUPLE}")
                    continue
                data = s.recv(19)
                bittorrent_protocol = data.decode()
                if bittorrent_protocol != "BitTorrent protocol":
                    logging.error("This is not talking in bittorrent protocol")
                protocol_version = s.recv(8)
                info_hash = s.recv(20)
                peer_id = s.recv(20)
                print(f"Connected with Peer_ID={peer_id}")
            except Exception as e:
                print(e)


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

    peers_data = parse_peers_data(peers_data)
    handshake = build_handshake(info_hash, random_peer_id, protocol_string)

    logging.info(f"{handshake}")

    fetch_pieces(peers_data, handshake)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
