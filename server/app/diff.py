import difflib
import json
import os
import re
from pathlib import Path
from typing import Dict, List

from app.models import Contract

BASE_CONTRACTS_PATH = "app/base_contracts/"


def get_closest_base_contract(new_contracts: List[Contract]) -> List[str]:
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

    closest_contracts: List[str] = []
    for contract in new_contracts:
        min_diffs = float("inf")
        closest_contract_name = os.listdir(BASE_CONTRACTS_PATH)[0]

        # Find closest base contract
        new_code = parse_contract_code(contract)[contract.name]
        for base_contract_name, base_contract in base_contract_name_to_code.items():
            num_diffs = _get_num_diffs(base_contract, new_code)
            if num_diffs < min_diffs:
                min_diffs = num_diffs
                closest_contract_name = base_contract_name
        closest_contracts.append(closest_contract_name)

    return closest_contracts


def contracts_to_code(source_str: str) -> Dict[str, str]:
    # Match any library, interface, or contract names
    file_regex = r"(library|interface|contract)\s+(\S+)\s*\{"
    matches = re.findall(file_regex, source_str)
    code = {}
    for match in matches:
        filetype, name = match
        code[name] = _get_code_from_file(source_str, filetype, name)
    return code


def parse_contract_code(contract: Contract) -> Dict[str, str]:
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


def _get_num_diffs(a, b):
    differ = difflib.Differ()
    diffs = differ.compare(a, b)

    num_diffs = 0
    for line in diffs:
        diff_code = line[:2]
        line_contents = line[2:]
        if diff_code in ["+ ", "- "] and line_contents.strip() != "":
            num_diffs += 1
    return num_diffs
