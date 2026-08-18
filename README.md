# certg

A certificate generator: takes one SVG template plus a list of people in a
CSV, and produces one PDF per person.

## What you need installed

- Python 3
- The Python packages in `requirements.txt` (`PyYAML` and `python-dotenv`)
- [Inkscape](https://inkscape.org/), which does the SVG → PDF conversion

## Setup

```bash
python3 -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

Then copy the environment template and point it at your Inkscape install:

```bash
cp .env.example .env
```

`.env` holds a single variable, `INKSCAPE_PATH`, which is the Inkscape
executable the script calls:

| System  | Usual value                                          |
| ------- | ---------------------------------------------------- |
| macOS   | `/Applications/Inkscape.app/Contents/MacOS/inkscape`  |
| Windows | `C:/Program Files/Inkscape/bin/inkscape.exe`          |
| Linux   | `inkscape`                                            |

If the variable is unset, the script falls back to plain `inkscape` (which
works when Inkscape is already on your `PATH`). If the path is wrong, the
script says so and stops before generating anything.

`.env` is gitignored, so each person on the team keeps their own.

## Running it

```bash
python certg.py certg.yaml
```

That reads three files — the config you passed, the SVG it names
(`template.svg` by default), and `attendance.csv` — and writes one PDF per
row of the CSV into the `output/` folder.

## The three input files

### 1. `attendance.csv` — who the certificates are for

The filename is **fixed**: the script always reads `attendance.csv` from the
folder you run it in. It cannot be renamed or passed as an argument.

It must contain two columns, `full_name` and `id`:

```csv
full_name,id
Ada Lovelace,12345678
Grace Hopper,87654321
```

| Column      | Becomes                | Notes                                    |
| ----------- | ---------------------- | ---------------------------------------- |
| `full_name` | `{{name}}`             | The full name as it should read on the certificate. |
| `id`        | `{{identification}}`   | The attendee's identification number.    |

Columns are matched **by their name in the header row**, so the order does
not matter and extra columns are ignored — if your registration tool exports
an `email` or `phone` column, you can leave it in the file and the script
will skip it. What it cannot do is guess: if a column is named something
else (`cedula` instead of `id`, say), the script stops and tells you which
name it could not find.

Spaces around the values are trimmed, so `Ada Lovelace, 12345678` and
`Ada Lovelace,12345678` are read the same way.

### 2. `certg.yaml` — the configuration

You can name this file whatever you like, since you pass it as the argument.
All four keys below are required:

```yaml
# Filename of the source SVG
svg_source: "template.svg"

# The prefix of all generated PDFs, and the variable name from the
# replace info to use as a distinction
result_prefix: 'certificado_django_girls'
result_distinct: 'name'

# Values that are the same on every certificate
result_event_data:
  event_name: 'Taller de programación para mujeres Medellín 2024'
  event_place_name: 'Universidad EAFIT'
  event_date: '01 de junio de 2024'
  event_start_hour: '8:30'
  event_end_hour: '17:00'
  event_city: 'Medellín'
```

| Key                 | What it does                                                                                                                            |
| ------------------- | --------------------------------------------------------------------------------------------------------------------------------------- |
| `svg_source`        | Filename of the SVG template to fill in.                                                                                                  |
| `result_prefix`     | First half of every output filename.                                                                                                      |
| `result_distinct`   | Which per-person value makes each filename unique. Only `name` or `identification` are valid — those are the only two the CSV provides.    |
| `result_event_data` | A dictionary of values shared by every certificate. Each key becomes a `{{placeholder}}` in the SVG. You can add or rename keys freely.    |

`result_event_data` is the one you will edit for each new event. The keys
listed above are not special — they are simply the ones `template.svg`
uses. Add a key here and a matching `{{key}}` in the SVG and it will be
filled in.

### 3. The SVG template

The template is a normal SVG with placeholders written in double curly
brackets. `template.svg` is the one to start from: an A4 landscape
certificate that is ready to use as it is, with every colour and font size
collected in a single `<style>` block so it is easy to restyle.

The project also includes `cert.svg`, the original Django Girls design.
Either one works — whichever you point `svg_source` at in your YAML.

Both use the same eight placeholders:

| Placeholder             | Comes from                          |
| ----------------------- | ----------------------------------- |
| `{{name}}`              | CSV, `full_name` column             |
| `{{identification}}`    | CSV, `id` column                    |
| `{{event_name}}`        | `result_event_data` in the YAML     |
| `{{event_place_name}}`  | `result_event_data`                 |
| `{{event_date}}`        | `result_event_data`                 |
| `{{event_start_hour}}`  | `result_event_data`                 |
| `{{event_end_hour}}`    | `result_event_data`                 |
| `{{event_city}}`        | `result_event_data`                 |

Note that the placeholder names are not identical to the CSV column names:
the `full_name` column fills `{{name}}`, and `id` fills `{{identification}}`.

Every value is **uppercased** before it is inserted, so `Ada Lovelace`
appears on the certificate as `ADA LOVELACE`.

A placeholder with no matching value is replaced with an empty string
rather than causing an error - so if a certificate comes out with a blank
where text should be, check for a typo in the placeholder name.

#### Editing the template

SVG text does not wrap, so each placeholder has to fit on one line.
In `template.svg` the font sizes are set so that roughly 32 characters fit
in `{{name}}` and 48 in `{{event_name}}`. A longer name or event title will
run past the border; the fix is to lower the matching `font-size` in the
`<style>` block at the top of the file. The colour, borders and signature
line live in that same block.

If you edit the template in Inkscape, be careful not to break the
placeholders: Inkscape can split a line of text into several `<tspan>`
elements, and a placeholder split across two of them will not be replaced.
It is worth re-checking they all survived:

```bash
grep -o '{{[a-z_]*}}' template.svg | sort -u
```

## Output

The PDFs are written to an `output/` folder, created automatically on the
first run. Each file is named `<result_prefix>-<result_distinct value>.pdf`,
with the distinct value lowercased and spaces turned into underscores.

With the config above, `Ada Lovelace` produces:

```
output/certificado_django_girls-ada_lovelace.pdf
```

The whole `output/` folder is gitignored, so generated certificates are
never committed - they usually contain personal data, so keep it that way.
Re-running the script overwrites files with the same name.

## Using it for your own event

1. Put your attendees into `attendance.csv`.
2. Start from `template.svg`, leaving the `{{placeholders}}` intact.
3. Update `result_event_data` in the YAML with your event's details.
4. Run `python certg.py certg.yaml`.
