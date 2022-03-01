import difflib
import json
import os
import re
from pathlib import Path
from typing import Dict, List, Union

from app.models import Contract

BASE_CONTRACTS_PATH = "app/base_contracts/"


def get_closest_base_contract(contracts: List[str]):
    base_contract_name_to_code = {}
    for name in os.listdir(BASE_CONTRACTS_PATH):
        base_contract_dir = os.path.join(BASE_CONTRACTS_PATH, name)
        files = os.listdir(base_contract_dir)
        file_strs = []
        for f in files:
            f_path = os.path.join(base_contract_dir, f)
            if os.path.isfile(f_path):
                file_strs.append(Path(f_path).read_text())
        code = contracts_to_code("\n".join(file_strs))[name]
        base_contract_name_to_code[name] = code

    for contract in contracts:
        # Find closest base contract
        pass


def contracts_to_code(source_str: str) -> Dict[str, str]:
    # Match any library, interface, or contract names
    file_regex = r"(library|interface|contract)\s+(\S+)\s*\{"
    matches = re.findall(file_regex, source_str)
    code = {}
    for match in matches:
        filetype, name = match
        code[name] = _get_code_from_file(source_str, filetype, name)
    return code


def parse_contract_code(contract: Contract) -> Union[str, None]:
    source_code_json = json.loads(contract.source_code)[0]["SourceCode"]
    if source_code_json[0] == "{" and source_code_json == "}":
        sources = json.loads(source_code_json[1:-1])
        source_str = ""
        for source in sources["sources"]:
            source_str += source["content"]
    else:
        source_str = source_code_json
    return contracts_to_code(source_str)


def _get_code_from_file(source_str: str, type: str, name: str):
    contract_regex = rf"{type}\s+{name}\s*{{"
    res = re.search(contract_regex, source_str)
    if not res:
        return None

    start_idx = res.start()
    # Position of starting brace + 1
    close_idx = res.end() + 1
    opened_braces = 1

    # Find closing bracket for contract
    while opened_braces > 0 and close_idx < len(source_str):
        if source_str[close_idx] == "{":
            opened_braces += 1
        elif source_str[close_idx] == "}":
            opened_braces -= 1
        close_idx += 1

    res = source_str[start_idx : min(close_idx + 1, len(source_str))]
    return res.strip("\\").replace("\\\\n", "\n").replace('\\\\"', '"')
