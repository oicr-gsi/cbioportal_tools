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

The schema may contain a `head` entry. In addition, the `head` entry may be an empty mapping.

If present and not empty, the `head` entry represents the YAML header of the Janus config file. Entries in the head are represented as YAML mappings.

The head has three types of entries:

1. `dictionary`: May contain any mixture of scalars, lists, or other dictionaries.
2. `constant_list`: Contains a simple collection of constants. It may _not_ contain entries for scalars, dictionaries, or other constant-lists. If a `constant_list` is present in a config file, it must have _exactly_ the same contents as in the schema.
3. `scalar`: Represents a scalar variable, such as a string or integer.

All entries **must** have:
- `type`: Respectively `scalar`, `constant_list` or `dictionary`.
- `required`: Boolean value. See "Note" below.

In addition, constant-lists and dictionaries **must** have:
- `contents`: Respectively, a YAML sequence or mapping to hold the contents of the constant-list or dictionary.

In addition, scalars **may** have:
- `description`: Optional string describing the variable.

#### Note on required entries

What if a dictionary has `required=false` but one or more of its children has `required=true`?

Then the dictionary does not have to be present; but if the dictionary _is_ present, then all children with `required=true` must also be present.

## Examples

- [Example schema](../src/test/data/schema/schema1.yaml)
- [Example template](../src/test/data/schema/example_template.txt)
