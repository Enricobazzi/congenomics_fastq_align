import argparse
import subprocess
from src import RunConfig
from src import map_reads
from src import sort_bam
from src import add_rg
from src import make_rg_bamlist
from src import merge_bams
from src import rename_to_merged_bam
from src import mark_dups
from src import index_bam
from src import realigner_target_creator
from src import indel_realigner
from src import print_sample_pipeline

def main(sample: str, config_file: str, test_script: bool = False):
    
    run = RunConfig(config_file)
    
    bash_script = f"{sample}_{run.alignment_name}_aligner.sh"
    
    # write the script that will run the alignment of the sample
    with open(bash_script, 'w') as f:
        f.write('#!/bin/bash\n') # Add a shebang line to make the file executable
        f.write('set -e\n') # Add a line to stop the script if any command fails
        f.write(print_sample_pipeline(sample = sample, run = run))
    
    # run the script
    if not test_script:
        subprocess.run(['echo', 'running alignment for', sample])
        subprocess.run(['bash', bash_script])
    else:
        return

if __name__ == '__main__':
    # parse arguments
    parser = argparse.ArgumentParser(
        description='ConGenomics pipeline for aligning fastqs of a sample to a reference genome'
    )
    
    parser.add_argument("--sample", help="the name of the sample to be analyzed")
    parser.add_argument("--config", help="the yaml file where the configuration parameters for the run are stored")
    parser.add_argument("--test", action="store_true", help="specify this argument if you wish to only generate the alignment bash script for your sample but not run it")
    
    args = parser.parse_args()
    
    config_file = args.config
    sample = args.sample
    
    if args.test:    
        main(sample, config_file, test_script = True)
    else:
        main(sample, config_file)