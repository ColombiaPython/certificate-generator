#!/usr/bin/env python3

# Copyright 2013 Facundo Batista
# This file is GPL v3, part of http://github.com/facundobatista/certg
# project; refer to it for more info.

import subprocess
import sys
import tempfile
import yaml
import csv


def get_names_and_id():
    dict_info = []
    with open('registro_asistentes.csv') as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=',')
        for line_count, row in enumerate(csv_reader):
            if line_count == 0:
                print(f'Column names are {", ".join(row)}')
            else:
                dict_info.append(
                    {
                        'name': row[3],
                        'identification': row[4]
                    }
                )
    return dict_info

def main():
    if len(sys.argv) != 2:
        print(f"Usage: {sys.argv[0]} <config.yaml>")
        exit()

    with open(sys.argv[1], 'rt', encoding="utf-8") as fh:
        config = yaml.safe_load(fh)

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
        result = "{}-{}.pdf".format(config['result_prefix'], distinct)

        # Below you need to add the route to the executable of inkscape
        # e.g Windows: C:/Program Files/Inkscape/inkscape.exe
        # e.g Mac: /Applications/Inkscape.app/Contents/MacOS/inkscape
        cmd = ["/Applications/Inkscape.app/Contents/MacOS/inkscape", '--export-pdf={}'.format(result), tmpfile]
        subprocess.check_call(cmd)
        print("Finished======")

if __name__ == '__main__':
    main()
