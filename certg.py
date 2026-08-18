#!/usr/bin/env python3

# Copyright 2013 Facundo Batista
# This file is GPL v3, part of http://github.com/facundobatista/certg
# project; refer to it for more info.

import os
import shutil
import subprocess
import sys
import tempfile
import yaml
import csv

from dotenv import load_dotenv

load_dotenv()

REQUIRED_CONFIG_KEYS = (
    'svg_source', 'result_prefix', 'result_distinct', 'result_event_data')

# Folder the generated PDFs are written to; created if it does not exist.
OUTPUT_DIR = 'output'


def get_names_and_id():
    """Read the attendees from attendance.csv, keyed by column name."""
    dict_info = []
    with open('attendance.csv', encoding="utf-8") as csv_file:
        csv_reader = csv.DictReader(csv_file)
        print(f'Column names are {", ".join(csv_reader.fieldnames or [])}')

        missing = {'full_name', 'id'} - set(csv_reader.fieldnames or [])
        if missing:
            print(f"attendance.csv is missing the column(s): "
                  f"{', '.join(sorted(missing))}")
            exit(1)

        for row in csv_reader:
            dict_info.append(
                {
                    'name': row['full_name'].strip(),
                    'identification': row['id'].strip()
                }
            )
    return dict_info

def get_inkscape():
    """Return the Inkscape executable, from INKSCAPE_PATH in the .env file."""
    inkscape = os.environ.get('INKSCAPE_PATH', 'inkscape')
    if shutil.which(inkscape) is None:
        print(f"Inkscape not found at {inkscape!r}.")
        print("Set INKSCAPE_PATH in your .env file; see .env.example for the "
              "usual location on each system.")
        exit(1)
    return inkscape


def get_config(filename):
    """Load and validate the YAML configuration file."""
    with open(filename, 'rt', encoding="utf-8") as fh:
        config = yaml.safe_load(fh)

    if not isinstance(config, dict):
        print(f"{filename} is not a valid configuration file.")
        print("Pass the YAML config, e.g. 'certg.yaml'; see the README.")
        exit(1)

    missing = [key for key in REQUIRED_CONFIG_KEYS if key not in config]
    if missing:
        print(f"{filename} is missing the setting(s): {', '.join(missing)}")
        print("See the README for what each one does.")
        exit(1)

    return config


def main():
    if len(sys.argv) != 2:
        print(f"Usage: {sys.argv[0]} <config.yaml>")
        exit()

    inkscape = get_inkscape()
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    config = get_config(sys.argv[1])

    with open(config['svg_source'], "rt", encoding="utf-8") as fh:
        content_base = fh.read()

    # Get replace info
    config['replace_info'] = get_names_and_id()

    # Get all the replacing attrs
    replacing_attrs = set()
    for data in config['replace_info']:
        replacing_attrs.update(data)

        # for data in config['replace_info']:
        content = content_base
        for attr in replacing_attrs:
            value = data.get(attr)
            if value is None:
                value = ""
            content = content.replace("{{" + attr + "}}", value.upper())
        for attr, value in config['result_event_data'].items():
            content = content.replace("{{" + attr + "}}", value.upper())


        _, tmpfile = tempfile.mkstemp()
        with open(tmpfile, "wt", encoding="utf-8") as fh:
            fh.write(content)

        distinct = data[config['result_distinct']].lower().replace(" ", "_")
        filename = "{}-{}.pdf".format(config['result_prefix'], distinct)
        result = os.path.join(OUTPUT_DIR, filename)

        cmd = [inkscape, '--export-type=pdf', f'--export-filename={result}', tmpfile]
        subprocess.check_call(cmd)
        print("Finished======")

if __name__ == '__main__':
    main()
