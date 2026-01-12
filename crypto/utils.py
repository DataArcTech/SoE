import os
import io
import json
from typing import Dict


def get_synthesized_data_from_json(data_path):
    # Open and read the JSON file
    with open(data_path, 'r') as file:
        data = json.load(file)

    return data

def insert_dash(line, idxs):
        offset = 0
        for i in range(len(idxs)):
            idx = idxs[i] + offset
            line = line[:idx] + '\\' + line[idx:]
            offset = offset + 1
        return line

def revise_synthesized_enti_json(input_path, output_path):
    """
    Fix the errors in coverted json file after encrypting the original json
    """
    # path = "data/person_encrypt My Father's Estate by Ben Stein.json"
    # output_path = "data/revised_person_encrypt My Father's Estate by Ben Stein.json"
    with open(input_path, "r") as f:
        lines = f.readlines()

    new_lines = []

    for line in lines:
        start = -1
        end = -1
        for i in range(len(line)):
            if line[i] == '"':
                start = i 
                break
        for i in range(len(line)):
            if line[len(line)-i-1] == '"':
                end = len(line)-i-1
                break
        print(start,end)
        if start == -1 or end == -1:
            new_lines.append(line)
            continue
        idx_list = []
        for i in range(start+1,end):
            # print(line[i])
            if line[i] == '"' and line[i-1] != '\\':
                idx_list.append(i)
        print(idx_list)
        nline = insert_dash(line,idx_list)
        new_lines.append(nline)

    with open(output_path, "w")  as f:
        for nline in new_lines:
            f.write(nline)
    return

def _make_w_io_base(f, mode: str, encoding="utf-8"):
    if not isinstance(f, io.IOBase):
        f_dirname = os.path.dirname(f)
        if f_dirname != "":
            os.makedirs(f_dirname, exist_ok=True)
        f = open(f, mode=mode, encoding=encoding)
    return f


def _make_r_io_base(f, mode: str):
    if not isinstance(f, io.IOBase):
        f = open(f, mode=mode)
    return f


def jdump(obj, f: str, mode="w", indent=4, default=str, encoding="utf-8"):
    """Dump a str or dictionary to a file in json format.

    Args:
        obj: An object to be written.
        f: A string path to the location on disk.
        mode: Mode for opening the file.
        indent: Indent for storing json dictionaries.
        default: A function to handle non-serializable entries; defaults to `str`.
    """
    if mode in ['a','a+']:
        lines = []
        if os.path.exists(f):
            with open(f, 'r') as f1:
                lines = json.load(f1)
        if isinstance(obj, (list, dict)):
            lines.extend(obj)
            obj = lines
        mode = 'w'
    f = _make_w_io_base(f, mode, encoding=encoding)
    if isinstance(obj, (dict, list)):
        json.dump(obj, f, indent=indent, default=default, ensure_ascii=False)
    elif isinstance(obj, str):
        f.write(obj)
    else:
        raise ValueError(f"Unexpected type: {type(obj)}")
    f.close()


def jload_list(f, mode="r"):
    """Load multiple JSON objects from a file."""
    objects = []
    with open(f, mode) as file:
        for line in file:
            obj = json.loads(line)
            objects.append(obj)
    return objects

def jload(f, mode="r"):
    """Load a .json file into a dictionary."""
    f = _make_r_io_base(f, mode)
    jdict = json.load(f)
    f.close()
    return jdict