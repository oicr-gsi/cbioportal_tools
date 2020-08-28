Janus schema
============

We define a _schema_ in order to specify the structure of a Janus config file.

The schema can be used to:
- Validate the syntax of existing files
- Generate a template for writing new files

## Schema format

The Janus schema is written in YAML format. Its structure is as follows:

### body

The schema must contain a `body` entry. This represents the tabular body of the Janus config file. Its value is a list of column headers, in the same order they are expected to appear in the config file.

### head

The schema must contain a `head` entry. This represents the YAML header of the Janus config file.

The head has two types of entries: `scalar` and `dictionary`. A `dictionary` may contain scalars, other dictionaries, or a mixture of both.

Scalars and dictionaries both have:
- A `type` entry, which is `scalar` or `dictionary` respectively.
- A `required` entry, which is a Boolean value.

In addition, dictionaries have:
- A `contents` entry, which holds the contents of the dictionary.

## Examples

- [Example schema](../src/test/data/schema/schema1.yaml)
- [Example template](../src/test/data/schema/example_template.txt)
