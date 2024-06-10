
# MARC Scanner

## Description
MARC Scanner is a python tool to scan MARC files in parallel and generate simple statistics and reports.
The Scanner loads records and passes them through Processors which can analyze the records to create reports or gather statistics.

This tool provides a framework to help process records and collect data by writing Processors in Python.

Run the tool with one or more MARC files as input to collect the data.

JSON, XML, and Binary MARC21 files can be used as input to the Scanner. The format is determined by the extension of the file.

## Requirements
Python >= 3.7 with venv

## Quick Start
```bash
clone <git repo>
cd marc_scanner
python3 -m venv .venv
. ./.venv/bin/activate
pip3 install -r requirements.txt
python3 marc_scanner.py samples/sample1_records.mrc -p Printer
python3 marc_scanner.py samples/sample1_records.mrc -p RecordCounter
python3 marc_scanner.py samples/sample1_records_interleave.mrc -p LocationGroups --interleave
python3 marc_scanner.py samples/sample1_records.mrc -p Collections710
python3 marc_scanner.py samples/sample1_records.mrc -p Exhibits711
python3 marc_scanner.py samples/sample1_records.mrc -p AsMarc
ls *.log
```

## Usage
```help
usage: marc_scanner.py [-h] -p PROCESSOR [-n MAX_WORKERS] [-i] files

Parse MARC Records and generate statistics and reports

positional arguments:
  files                 MARC file(s) to process using file globbing (reads binary MARC, MARC-XML, and MARC-JSON)

options:
  -h, --help            show this help message and exit
  -p PROCESSOR, --processor PROCESSOR
                        processor(s) (comma separated list)
  -n MAX_WORKERS, --max-workers MAX_WORKERS
                        maximum number of workers
  -i, --interleave      interleave bibs followed by holdings (files must be interleaved)
  ```

## Writing Processors
Processors receive MARC records and analyze them to collect information or write to files.
There are example processors in [./processors](./processors/) or subdirectories.

Write and add your own processors to `./processors` or a subdirectory of `./processors`.

Processors can either process records one at a time or receive groups of bibs and related holdings if files are interleave records.

All processors are subclasses of `BaseProcessor` with the same constructor. They implement at lease one of the `marc_record` processing methods to read and process each record.

### Record Processing
Use `def marc_record(self, record):` to receive one record at a time and process them individually.

### Interleave Processing
Use `def marc_record_group(self, records):` to receive groups of records containing a bib and all holdings that follow it in the MARC
files. The script must be run with the `--interleave` argument to use this method. The MARC files being read must be in interleave format
with each bib followed by all of its holdings.

### Writing to Files
The Processor is constructed with a Reporter which is created by the Scanner. The Reporter makes it easy to write to files.
File creation and close is handled by the reporter.

#### Writing to Report Files

`Reporter.write_line(<filename>, <str>)` will write the string to the file. The Reporter also uses locks to make sure there is no concurrent writing to the file.

`Reporter.write_line(<filename>, <array>)` will join the array with TABs and write it to the file.

#### Writing to MARC Files
`Reporter.write_marc(<filename>, <pymarc record>)` write a MARC record to the file. The type of MARC file is determined by the filename's extension.
See the [./processors/as_marc.py](./processors/as_marc.py) example Processor.

### Collecting Statistics
The Reporter also collects simple statistics and prints a simple text based report when the scanner is complete. The Reporter takes
care of concurrency and storing the counts

#### `add_count(<str>)`


#### `add_count_value(<str>, <str>)`