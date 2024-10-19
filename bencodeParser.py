from typing import Any, List, Tuple
from typing import Dict


def parse_int(data: str, idx: int) -> Tuple[int, int]:
    idx += 1
    value = ""
    while data[idx] != "e":
        value += data[idx]
        idx += 1

    return (int(value), idx)


def parse_binary(data: str, idx: int) -> Tuple[str, int]:
    print("parsing binary")
    value = ""

    # add plus 1 because of the semi colon
    binary_string_size = int(data[idx])

    print(f"tamanho da string binaria {binary_string_size}")

    idx += 2
    idx_string = 0

    while idx_string < binary_string_size:
        value += data[idx + idx_string]
        idx_string += 1

    print(value)
    return (value, idx + idx_string - 1)


def parse_list(data: str, idx: int) -> Tuple[List, int]:
    res = []
    idx += 1
    current_elem: str = data[idx]

    while current_elem != "e":
        print(f"inside parse_list {current_elem}")
        value = None

        if current_elem.isdigit():
            value, new_idx = parse_binary(data, idx)
            res.append(value)
            idx = new_idx

        elif current_elem == "i":
            value, new_idx = parse_int(data, idx)
            res.append(value)
            idx = new_idx

        elif current_elem == "l":
            value, new_idx = parse_list(data, idx)
            res.append(value)
            idx = new_idx

        elif current_elem == "d":
            value, new_idx = parse_dict(data, idx)
            res.append(value)
            idx = new_idx

        print(f"Last parsed value {value} new idx {idx}")

        idx += 1
        current_elem: str = data[idx]

    return res, idx


def parse_dict(data: str, idx: int) -> Tuple[Dict, int]:
    res = {}
    idx += 1
    current_elem: str = data[idx]

    while current_elem != "e":
        dict_key_size = int(current_elem)
        idx += 2

        print(dict_key_size)

        key = data[idx : idx + dict_key_size]
        print(f"Dict Key {key}")
        idx += dict_key_size
        print(f"next {data[idx]}")

        current_elem = data[idx]
        value = None

        if current_elem == "i":
            # integer found
            value, new_idx = parse_int(data, idx)
            print(value)
            idx = new_idx

        elif current_elem.isdigit():
            value, new_idx = parse_binary(data, idx)
            idx = new_idx

        elif current_elem == "l":
            value = []
            value, new_idx = parse_list(data, idx)
            idx = new_idx

        elif current_elem == "d":
            value = {}
            value, new_idx = parse_dict(data, idx)
            idx = new_idx
        else:
            raise ValueError(f"Value not mapped in main loop {current_elem}")

        print(f"adicionando a key {key} e o valor {value}")
        res[key] = value

        idx += 1
        current_elem = data[idx]

    return (res, idx)


def parser(data: str) -> Any:
    idx = 0

    result = []

    while True:
        current_elem: str = data[idx]

        if current_elem == "i":
            # integer found
            value, new_idx = parse_int(data, idx)
            result.append(value)
            print(value)
            idx = new_idx

        elif current_elem.isdigit():
            value, new_idx = parse_binary(data, idx)
            result.append(value)
            idx = new_idx

        elif current_elem == "l":
            value = []
            value, new_idx = parse_list(data, idx)
            idx = new_idx

            result.append(value)

        elif current_elem == "d":
            value = {}
            value, new_idx = parse_dict(data, idx)
            idx = new_idx
            result.append(value)

        else:
            raise ValueError(f"Value not mapped in main loop {current_elem}")

        idx += 1
        if idx >= len(data):
            break

    return result


parser("i42ei32ei40e3:AAAi42e4:WAGA")
print("****")

print(parser("ll4:spami42ee4:spami42ee"))
#
TEST = "d3:bar4:spam3:fooi42ee"
print(TEST)
print(parser(TEST))
TEST = "d3:abcld3:bar4:spam3:fooli42ei300ei400eeeee"

print(TEST)
print(parser(TEST))
