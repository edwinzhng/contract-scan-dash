import difflib
import json
import re
from typing import Union

from app.models import Contract


def compute_diff(file_a, file_b):
    pass


def get_base_contract(contract: Contract) -> Union[str, None]:
    source_code_json = json.loads(contract.source_code)[0]["SourceCode"]
    if source_code_json[0] == "{" and source_code_json == "}":
        sources = json.loads(source_code_json[1:-1])
        source_str = ""
        for source in sources["sources"]:
            try:
                print(json.loads(source_code_json))
            except Exception as e:
                print(e)
            source_str += source["content"]
    else:
        source_str = source_code_json

    contract_regex = rf"contract\s+{contract.name}\s+{{"
    res = re.search(contract_regex, source_str)
    if not res:
        return None

    start_idx = res.start()
    # Position of starting brace + 1
    close_idx = res.end() + 1
    opened_braces = 1

    # Find closing bracket for base contract
    while opened_braces > 0 and close_idx < len(source_str):
        if source_str[close_idx] == "{":
            opened_braces += 1
        elif source_str[close_idx] == "}":
            opened_braces -= 1
        close_idx += 1

    res = source_str[start_idx : min(close_idx + 1, len(source_str))]
    return res.strip("\\").replace("\\\\n", "\n").replace('\\\\"', '"')
