#!/usr/bin/env python
import os
import glob
import linecache
import subprocess
import hashlib
import yaml
import click
import logging
import sys
import json

from yapf.yapflib.yapf_api import FormatFile

from BALSAMIC.config.sample import get_config
from BALSAMIC.config.sample import write_json
from BALSAMIC.workflows.run_analysis import get_sample_name
from BALSAMIC.workflows.run_analysis import get_analysis_dir


@click.command(
    "report", short_help="Create a report config file for report generation.")
@click.option(
    '-s',
    '--sample-config',
    required=True,
    type=click.Path(),
    help='Sample json config file.')
@click.option(
    '-o',
    '--output-config',
    required=True,
    type=click.Path(),
    help='Path to output config file to write.')
@click.pass_context
def report(context, sample_config, output_config):
    """
    Prepares a config file for balsamic config report to export results as pdf

    """

    config_json = json.load(open(sample_config))

    json_out = dict()

    json_out["analysis"] = dict()
    json_out["analysis"]["sample_id"] = get_sample_name(sample_config)
    json_out["analysis"]["analysis_dir"] = os.path.join(
        get_analysis_dir(sample_config, "analysis_dir"),
        get_sample_name(sample_config))

    json_out["bed"] = dict()
    genome_size = list()
    target_line_num = 5

    hsmetric_files = glob.glob(
        os.path.join(json_out["analysis"]["analysis_dir"], "results", "qc",
                     "*hsmetric.csv"))
    for i in hsmetric_files:
        genome_size.extend(
            linecache.getline(i, target_line_num).split("\t")[1:-1])

    json_out["bed"]["genome_size"] = list(set(genome_size))[0]

    json_out["bed"]["exon_cov"] = dict()
    for i in config_json["samples"]:
        json_out["bed"]["exon_cov"][i] = "".join(
            glob.glob(
                os.path.join(
                    get_analysis_dir(sample_config, "analysis_dir"),
                    get_sample_name(sample_config), "results", "bam",
                    config_json["samples"][i]["file_prefix"] +
                    "*exon.cov.bed")))

    json_out["vcf"] = dict()
    json_out["vcf"]["merged"] = dict()
    json_out["vcf"]["merged"]["SNV"] = os.path.join(
        get_analysis_dir(sample_config, "analysis_dir"),
        get_sample_name(sample_config), "results", "vep",
        "vep_SNV.merged.table")

    write_json(json_out, output_config)
    FormatFile(output_config, in_place=True)