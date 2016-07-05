#!/usr/bin/env python

#from sumatra.projects import load_project
#from sumatra.parameters import build_parameters
#from sumatra.decorators import capture
from ruffus import *
import sys 
import os
import time
import datetime 
import drmaa
from omics_pipe.utils import *
from omics_pipe.modules.fastqc import fastqc
from omics_pipe.modules.star_miRNA import star_miRNA
from omics_pipe.modules.htseq_miRNA import htseq_miRNA
from omics_pipe.modules.RNAseq_report_counts import RNAseq_report_counts
from omics_pipe.modules.fastq_length_filter_miRNA import fastq_length_filter_miRNA
from omics_pipe.modules.cutadapt_miRNA import cutadapt_miRNA


from omics_pipe.parameters.default_parameters import default_parameters 
p = Bunch(default_parameters)


os.chdir(p.WORKING_DIR)
now = datetime.datetime.now()
date = now.strftime("%Y-%m-%d %H:%M")    

print p

for step in p.STEPS:
    vars()['inputList_' + step] = []
    for sample in p.SAMPLE_LIST:
        vars()['inputList_' + step].append([sample, "%s/%s_%s_completed.flag" % (p.FLAG_PATH, step, sample)])
    print vars()['inputList_' + step]

@parallel(inputList_cutadapt_miRNA)
@check_if_uptodate(check_file_exists)
def run_cutadapt_miRNA(sample, cutadapt_miRNA_flag):
    cutadapt_miRNA(sample, cutadapt_miRNA_flag)
    return

@parallel(inputList_fastq_length_filter_miRNA)
@check_if_uptodate(check_file_exists)
@follows(run_cutadapt_miRNA)
def run_fastq_length_filter_miRNA(sample, fastq_length_filter_miRNA_flag):
    fastq_length_filter_miRNA(sample, fastq_length_filter_miRNA_flag)
    return
   

@parallel(inputList_fastqc)
@check_if_uptodate(check_file_exists)
@follows(run_fastq_length_filter_miRNA)
def run_fastqc(sample, fastqc_flag):
    fastqc(sample, fastqc_flag)
    return

@parallel(inputList_star_miRNA)
@check_if_uptodate(check_file_exists)
def run_star_miRNA(sample, star_miRNA_flag):
    star_miRNA(sample, star_miRNA_flag)
    return


@parallel(inputList_htseq_miRNA)
@check_if_uptodate(check_file_exists)
@follows(run_star_miRNA)
def run_htseq_miRNA(sample, htseq_miRNA_flag):
    htseq_miRNA(sample, htseq_miRNA_flag)
    return

@parallel(inputList_RNAseq_report_counts)
@check_if_uptodate(check_file_exists)
@follows(run_fastqc, run_htseq_miRNA)
def run_RNAseq_report_counts(sample, RNAseq_report_counts_flag):
    RNAseq_report_counts(sample, RNAseq_report_counts_flag)
    return


@parallel(inputList_last_function)
@check_if_uptodate(check_file_exists)
@follows(run_RNAseq_report_counts)
def last_function(sample, last_function_flag):
    print "PIPELINE HAS FINISHED SUCCESSFULLY!!! YAY!"
    pipeline_graph_output = p.FLAG_PATH + "/pipeline_" + sample + "_" + str(date) + ".pdf"
    pipeline_printout_graph (pipeline_graph_output,'pdf', step, no_key_legend=False)
    stage = "last_function"
    flag_file = "%s/%s_%s_completed.flag" % (p.FLAG_PATH, stage, sample)
    open(flag_file, 'w').close()
    return   


if __name__ == '__main__':

    pipeline_run(p.STEP, multiprocess = p.PIPE_MULTIPROCESS, verbose = p.PIPE_VERBOSE, gnu_make_maximal_rebuild_mode = p.PIPE_REBUILD)

