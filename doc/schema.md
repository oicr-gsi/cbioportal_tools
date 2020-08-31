Janus schema
============

We define a _schema_ in order to specify the structure of a Janus config file.

The schema can be used to:
- Validate the syntax of existing files
- Generate a template for writing new files

## Schema format

The Janus schema is written in YAML format. The basic structure is a mapping with two key/value pairs: `body` and `head`.

### body

The schema must contain a `body` entry. This represents the tabular body of the Janus config file. Its value is a sequence of column headers, in the same order they are expected to appear in the config file.

### head

The schema must contain a `head` entry. This represents the YAML header of the Janus config file. Entries in the head are represented as YAML mappings.

The head has two types of entries: `scalar` and `dictionary`. A `dictionary` may contain scalars, other dictionaries, or a mixture of both.

Scalars and dictionaries both **must** have:
- `type`: Respectively `scalar` or `dictionary`
- `required`: Boolean value. If true, the entry is required. See "Note" below.

In addition, dictionaries **must** have:
- `contents`: A mapping which holds the contents of the dictionary.

In addition, scalars **may** have:
- `description`: Optional string describing the variable.

#### Note on required entries

What if a dictionary has `required=false` but one or more of its children has `required=true`?

Then the dictionary does not have to be present; but if the dictionary _is_ present, then all children with `required=true` must also be present.

## Examples

- [Example schema](../src/test/data/schema/schema1.yaml)
- [Example template](../src/test/data/schema/example_template.txt)
