# tools
The folder holding the main program of all 4 of Janus' faces.
Each face is a standalone program that works without the others.

## Generator

The largest face([`generator.py`](generator.py)) generates a valid cBioPortal from input data such as:
* `.vcf`
* `.seg`
* `.maf`

This face also requires configuration files that will allow for the conversion process to take place.

## Import

The second face is the [`import.py`](importer.py) face. 
This face takes a ready study and uploads it to a target instance of cBioPortal.
This face can also take a complete `gene-panel` and upload it to a target instance.

## Remove

The third face of cBiorprtal is [`remove.py`](remove.py).
This face will take a target `study_id` and remove it from a cBioPortal instance.

## Query

The fourth and final face of cBioPortal is [`query.py`](query.py).
This face will query cBioPortal, as of now it only queries `cancer-type`s and `gene-panel`s.
However it should not be difficult to extend and query other tables.