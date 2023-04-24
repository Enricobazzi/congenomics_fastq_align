# congenomics_fastq_align - A tool to align reads to a reference genome

This is my first try to create a python package. It should be used to align fastq reads to a 
reference genome and process the resulting BAM file, according to our research group general 
protocol, using the [run_alignment](./run_alignment.py) python executable as follows:

```
python ./run_alignment.py --sample <sample_name> --config <config_file.yml>
```

-----------
# Getting Started

In order to run you need to make sure you have a few things already installed on your system:

- [python](https://www.python.org/)
- [conda](https://www.anaconda.com/)
- [bwa](https://arxiv.org/abs/1303.3997)
- [samtools](https://samtools.sourceforge.net/)
- [picard tools](http://broadinstitute.github.io/picard/)
- [GATK v.3.x](https://genome.cshlp.org/content/20/9/1297)

Then you should download and unzip the contents of this folder:

[latest release](https://github.com/Enricobazzi/congenomics_fastq_align/releases/latest)

Once the folder is downloaded you should be able to create a new conda environment with the required packages:

```
conda create --name <env_name> --file requirements.txt
```

and activate it:

```
conda activate <env_name>
```

The environment should now be ready for you to run the run_alignment.py script

-----------
# Configuration of the run

The information required in order to perform a full alignment of all of the fastq files of a samples should be stored in a YAML file. I've included both a [template](./config/template.yml) and an [example](./config/example.yml) inside the config folder.

Let's go over its individual components:

### *sample_dict*

This is a nested dictionary containing the sample name, mapped to its unique fastq_ids which are further mapped to the names of the pair end (R1 and R2) fastq files and the folder where they are stored, looking like this:

```
sample_dict:
  sample1: 
    id1:
      ['path/to/fastqs', 'id1_1.fastq.gz', 'id1_2.fastq.gz']
    id2:
      ['path/to/fastqs2','id2_1.fastq.gz', 'id2_2.fastq.gz']
```

Information regarding multiple samples can be stored in the same dictionary to make it easier to run the alignment to the same reference genome of multiple samples using the same configuration file.

### *reference_fasta*

This is the fasta file that we want to use as reference genome and align our reads to. Make sure that it is properly indexed for bwa to work by running:

```
bwa index <reference_fasta>
```

before starting the alignment process.

### *output_folder*

This is the path to the folder where the output files should be stored

### *threads*

Many commands in the pipeline have options for parallel computing. You can indicate the numer of threads you want them to use here.

### *alignment_name*

Give your alignment run a unique name in order to distinguish it from other alignments of the same sample. I usually indicate the reference genome it was aligned and its version (e.g. *Felis catus* version 9.0 -> FeCa_9.0_ref)

### *call_bwa*, *call_samtools*, *call_picard* and *call_gatk*

These should be the commands needed to execute bwa, samtools, picard and gatk or the paths to used to call these tools

-----------
# How does the pipeline work

Using the information stored in the configuration file, the [run_alignment](./run_alignment.py) script will create a new custom bash script for aligning reads of the specified sample, and execute it. The custom bash script, named  ```<sample_name>_<alignment_name>_aligner.sh```, will be created in the directory where you are running the python script, taking the alignment_name from the configuration yaml file.

The bash script will contain the following steps:

- for each fastq r1-r2 pair of the sample:
  - (a) *bwa-mem* + *samtools view* to align reads and spit out bam file
  - (b) *samtools sort* to sort the bam file
  - (c) *picardtools AddOrReplaceReadGroups* to add read groups to the bam file
- *samtools merge* to merge the bam files from the multiple R1-R2 pairs of the sample if necessary
- *picardtools MarkDuplicates* to mark duplicate reads in the bam
- realign indels which comprises:
  - (a) *samtools index* to index the bam
  - (b) *gatk RealignerTargetCreator* to identify realign targets
  - (c) *gatk IndelRealigner* to realign the indels
- *samtools index* to index the indel realigned bam for downstream analyses

In case you want to check the bash script before executing it you can add the ```--test``` flag to your [run_alignment](./run_alignment.py) command execution as such:
```
python ./run_alignment.py --sample <sample_name> --config <config_file.yml> --test
```
This will generate the bash script without executing it, so you can consult it beforehand.
