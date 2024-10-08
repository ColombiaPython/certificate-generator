# certg

A certificate generator, from a SVG to a lot of PDFs

## How to see an example

Get the code, and run:

````bash
python3 certg.py certg.yaml
````

The `certg.yaml` is included in the project, with the
other file it uses: `cert.svg`.

After successful execution, you will get two `.pdf` files,
the result of the generation.

## What do I need to have installed

The Python\'s module [yaml]() and [Inkscape]() in
your system.

## How to really use it, you mean, for my stuff

You need to create two files: the configuration, and the source SVG.
Here\'s a deep explanation of how it all works, but remember you can get
the examples provided and start tweaking them :)

The source SVG is the SVG you want to transform into PDFs, but with some
indications for text to be replaced in. These indications are between
curly brackets. For example, you may have:
```
Thanks {{name}} for all your {{type_of_doing}}!
```
Then, in the configuration file you have a `replace_info`
variable: it\'s a list of dictionaries. Each dictionary will produce a
generated PDF with the info replaced, and the keys/values in that
dictionary will be the info to replace.

Note that you need to provide in the config all the attributes to
replace; for example:
```
name: Foo Bar
type_of_doing: support
```
Furthermore, in the config you have some mandatory variables you need to
fill. Those are:

> -   `svg_source`: the filename of the SVG you created
> -   `result_prefix`: the prefix of the PDFs\' filenames that will be
>     generated
> -   `result_distinct`: the name of the variable in the replacing
>     attributes used as a distinct string for the PDFs.

For example, if you put `certs` as the prefix and
`name` as the distinct value, you\'ll get as output a file
named `certs-foobar.pdf`.

## Something important

It seems that along the way a new feature was added and never documented.
The current state of the script expects an `attendance.csv` file. 
There youll be able to easily populate the fields:

```csv
email, name, lastname, fullname, idnumber
```

As long as this csv file is found in the same folder, the script will
 find it and use it. Hope