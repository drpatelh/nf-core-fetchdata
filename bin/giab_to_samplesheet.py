#!/usr/bin/env python


import os
import sys
import errno
import argparse


def parse_args(args=None):
    Description = "Convert Genome In a Bottle samplesheet to nf-core/fetchdata format."
    Epilog = "Example usage: python giab_to_samplesheet.py <FILE_IN> <FILE_OUT>"

    parser = argparse.ArgumentParser(description=Description, epilog=Epilog)
    parser.add_argument("FILE_IN", help="Input samplesheet file.")
    parser.add_argument("FILE_OUT", help="Output file.")
    return parser.parse_args(args)


def make_dir(path):
    if len(path) > 0:
        try:
            os.makedirs(path)
        except OSError as exception:
            if exception.errno != errno.EEXIST:
                raise exception


def print_error(error, context="Line", context_str=""):
    error_str = "ERROR: Please check samplesheet -> {}".format(error)
    if context != "" and context_str != "":
        error_str = "ERROR: Please check samplesheet -> {}\n{}: '{}'".format(
            error, context.strip(), context_str.strip()
        )
    print(error_str)
    sys.exit(1)


def giab_to_samplesheet(file_in, file_out):
    """
    This function checks that the samplesheet follows the following structure:

    FASTQ	FASTQ_MD5	PAIRED_FASTQ	PAIRED_FASTQ_MD5	NIST_SAMPLE_NAME
    ftp://ftp-trace.ncbi.nih.gov/ReferenceSamples/giab/data/NA12878/Garvan_NA12878_HG001_HiSeq_Exome/NIST7035_TAAGGCGA_L001_R1_001.fastq.gz	630c611d62d995c5aeb60211add2f26e	ftp://ftp-trace.ncbi.nih.gov/ReferenceSamples/giab/data/NA12878/Garvan_NA12878_HG001_HiSeq_Exome/NIST7035_TAAGGCGA_L001_R2_001.fastq.gz	0b9c9976707eebe9a4a2d196afdbe1bd	HG001
    ftp://ftp-trace.ncbi.nih.gov/ReferenceSamples/giab/data/NA12878/Garvan_NA12878_HG001_HiSeq_Exome/NIST7035_TAAGGCGA_L002_R1_001.fastq.gz	d971c4e5311189026e54860b0671ca91	ftp://ftp-trace.ncbi.nih.gov/ReferenceSamples/giab/data/NA12878/Garvan_NA12878_HG001_HiSeq_Exome/NIST7035_TAAGGCGA_L002_R2_001.fastq.gz	11a02bee0645988109ca65ea817d53b4	HG001

    For an example see:
    https://raw.githubusercontent.com/genome-in-a-bottle/giab_data_indexes/master/NA12878/sequence.index.NA12878_Illumina_HiSeq_Exome_Garvan_fastq_09252015
    """

    sample_mapping_dict = {}
    with open(file_in, "r") as fin:
        HEADER = ['FASTQ', 'FASTQ_MD5', 'PAIRED_FASTQ', 'PAIRED_FASTQ_MD5', 'NIST_SAMPLE_NAME']
        header = [x.strip() for x in fin.readline().strip().split("\t")]
        if header[: len(HEADER)] != HEADER:
            print("ERROR: Please check samplesheet header -> {} != {}".format(",".join(header), ",".join(HEADER)))
            sys.exit(1)

        ## Check sample entries
        for line in fin:
            lspl = [x.strip().strip() for x in line.strip().split("\t")]

            # Check valid number of columns per row
            if len(lspl) != len(HEADER):
                print_error(
                    "Invalid number of columns (minimum = {})!".format(len(HEADER)),
                    "Line",
                    line,
                )

            ## Check sample name entries
            fastq_1, md5_1, fastq_2, md5_2, sample = lspl[: len(HEADER)]
            if not sample:
                print_error("Sample entry has not been specified!", "Line", line)

            if sample not in sample_mapping_dict:
                sample_mapping_dict[sample] = []
            sample_mapping_dict[sample].append([fastq_1, fastq_2, md5_1, md5_2])

    ## Write to file
    if sample_mapping_dict:
        with open(file_out, "w") as fout:
            fout.write(",".join(['sample', 'fastq_1', 'fastq_2', 'md5_1', 'md5_2']) + "\n")
            for sample in sorted(sample_mapping_dict.keys()):
                for idx,file_list in enumerate(sample_mapping_dict[sample]):
                    fout.write(",".join([sample + f'_RUN{idx+1}'] + file_list) + "\n")


def main(args=None):
    args = parse_args(args)
    giab_to_samplesheet(args.FILE_IN, args.FILE_OUT)


if __name__ == "__main__":
    sys.exit(main())
