import argparse
import os
import sys
import subprocess

def createParser():
    parser = argparse.ArgumentParser(description=arg_descriptions['prolog'], epilog=arg_descriptions['epilog'])
    parser.add_argument('-f', '--folder', required=True, help=arg_descriptions['folder'])
    parser.add_argument('-t', '--threads', required=True, help=arg_descriptions['threads'])
    parser.add_argument('-r', '--ref', required=True, help=arg_descriptions['ref'])
    parser.add_argument('-p', '--machine', required=True, help=arg_descriptions['machine'])
    parser.add_argument('-m', '--mode', required=True, help=arg_descriptions['sequence_mode'])
    parser.add_argument('-s', '--module', default='all', help=arg_descriptions['module'])
    parser.add_argument('--exclude_samples', default=[], help=arg_descriptions['exclude_samples'])
    parser.add_argument('--include_samples', default=[], help=arg_descriptions['include_samples'])
    return parser

def list_from_str(string):
    if type(string) == list:
        return string
    else:
        return string.split(',')

def get_env_list(machine:str):
    if machine == 'medgen':
        envs = {'samtools':'genetico',
                'freebayes':'genetico',
                'multiqc':'genetico',
                'cravat':'cravat'}
        binaries = {'trim_galore':'trim_galore',
                    'trimmomatic':'/usr/share/java/trimmomatic-0.39.jar',
                    'fastqc':'fastqc',
                    'samblaster':'samblaster',
                    'samtools': 'samtools',
                    'abra2':'-Xmx48G -jar /root/miniforge3/envs/genetico/share/abra2-2.24-1/abra2.jar',
                    'freebayes': 'freebayes',
                    'multiqc':'multiqc',
                    'cravat':conda_run(envs['cravat'], 'oc')}
    else:
        envs = {'trim-galore' : 'trim_galore', \
        'fastqc':'fastqc', \
        }
        binaries = {'trim_galore':conda_run(envs['trim_galore'], 'trim_galore'), 
                    'trimmomatic':'/home/medgen/programms/trimmomatic/trimmomatic-0.39.jar',
                    'fastqc': conda_run(envs['fastqc'], 'fastqc'),
                    'samblaster':'~/github/samblaster/samblaster',
                    'samtools':'samtools',
                    'abra2':'-Xmx12G -jar ~/miniforge3/envs/abra2/share/abra2-2.24-3/abra2.jar',
                    'freebayes': 'freebayes',
                    'multiqc':'multiqc'}
    return envs, binaries

def get_folders(dir:str):
    res_dir = f'{dir}result_pipeline/'
    qc_dir = f'{res_dir}QC/'
    bam_dir = f'{res_dir}bam/'
    vcf_dir = f'{res_dir}vcf/'
    ann_dir = f'{res_dir}annotation/'
    excel_dir = f'{res_dir}excel/'
    tmp_dir = f'{dir}tmp/'

    os.makedirs(tmp_dir, exist_ok=True)
    os.makedirs(bam_dir, exist_ok=True)
    os.makedirs(vcf_dir, exist_ok=True)
    os.makedirs(ann_dir, exist_ok=True)
    os.makedirs(excel_dir, exist_ok=True)
    os.makedirs(f'{qc_dir}multiqc/', exist_ok=True)
    
    return res_dir, tmp_dir, bam_dir, vcf_dir, qc_dir, ann_dir, excel_dir

def conda_run(env, command):
   return f'conda run -n {env} {command}'

def run_pipeline(module='all', include_samples=[], exclude_samples=[]):
    print(f'Module: {module}')
    cmd_data = generate_cmd_data(module, include_samples, exclude_samples)
    for sample in cmd_data.keys():
        print(f'Sample: {sample.split("/")[-1]}')
        for cmd_name in cmd_data[sample].keys():
            command = cmd_data[sample][cmd_name][0]
            cmd_args = cmd_data[sample][cmd_name][1]
            shell_command = command.format(*cmd_args)
            result = run_command(shell_command, cmd_name, sample)
            if result != 0:
                return f'ERROR! {cmd_name} failed, exit code: {result}'
                #raise Exception(f'{sample} failed on {module}: {result}')
            else:
                print(f'{cmd_name}: OK')
    return None

def generate_cmd_data(module, include_samples, exclude_samples):
    in_dir, source_extension = stage_vars[module][0], stage_vars[module][2]
    samples = generate_sample_list(in_dir, include_samples, exclude_samples, source_extension)
    #print(samples)
    cmd_data = {}
    for sample in samples:
        commands = generate_commands(sample, module)
        cmd_data.update({sample:commands})
    #print(cmd_data)
    return cmd_data

def generate_sample_list(in_dir, include_samples, exclude_samples, source_extension):
    samples = [s for s in os.listdir(in_dir) if s.endswith(source_extension)]
    if len(include_samples) != 0:
        samples =  [s for s in samples if any(inclusion in s for inclusion in include_samples)]
    if len(exclude_samples) != 0:
        samples =  [s for s in samples if not any(exclusion in s for exclusion in exclude_samples)]
    return [f'{in_dir}{s}' for s in samples]

def generate_commands(sample:str, module:str):
    filename = sample.split('/')[-1]
    #print(filename)
    basename = f'{filename.split("_")[0]}_{filename.split("_")[1]}'
    raw_fastqs = [sample, sample.replace('_R1', '_R2')]
    trim_galore_fastqs = [s.replace(dir, tmp_dir).replace('.fastq.gz', f'_val_{(raw_fastqs.index(s)+1)}.fq.gz') for s in raw_fastqs]
    trimmomatic_fastqs = ' '.join([f'{tmp_dir}{basename}_{i}P.fq' for i in [1,2]])
    abra_bam = f'{bam_dir}{basename}_abra2.bam'
    in_bam = f'{tmp_dir}primary.bam'
    sorted_bam = f'{tmp_dir}sorted.bam'
    vcf_freebayes = f'{vcf_dir}{basename}_freebayes.vcf'
    vcf_deepvariant = f'{vcf_dir}{basename}_deepvariant.vcf.gz'
    gvcf_deepvariant = vcf_deepvariant.replace('vcf','gvcf')
    annovar_vcf_mask = f'{annotation_dir}{basename}_annovar'

    all_cmds = {'trim_galore':['{} --length 35 --output_dir {} --cores {} --paired {}',
                            [binaries['trim_galore'], tmp_dir, threads, ' '.join(raw_fastqs)]],
            
            'trimmomatic':['java -jar {} PE -threads {} {} -baseout {}{}.fq SLIDINGWINDOW:4:20 HEADCROP:15 MINLEN:35',
                                [binaries['trimmomatic'], threads, ' '.join(trim_galore_fastqs), tmp_dir, basename]],
            
            'fastqc':['{} --quiet --threads 2 -o {} {}{}*P.fq',
                        [binaries['fastqc'], qc_dir, tmp_dir, basename]],
            
            'aligning':['bwa mem -t {} -M {} {} | {} -M -e -r -q --addMateTags | {} view -@ {} -Sb - > {}primary.bam',
                    [threads, ref_fasta, trimmomatic_fastqs, binaries['samblaster'], binaries['samtools'], threads, tmp_dir]],
            
            'samtools_sort':['{} sort -@ {} {} > {}',
                                [binaries['samtools'], threads, in_bam, sorted_bam]],
            
            'samtools_index':['{} index {}',
                                [binaries['samtools'], sorted_bam]],
            #export LC_ALL=en_US.UTF-8
            'abra2':['java {} --log error --in {} --out {} --ref {} --threads {} --tmpdir {}',
                        [binaries['abra2'], sorted_bam, abra_bam, ref_fasta, threads, tmp_dir]],

            'samtools_index_abra':['{} index {}',
                                [binaries['samtools'], abra_bam]],

#            'freebayes':['{} -f {} --standard-filters --report-genotype-likelihood-max --min-coverage 18 --min-alternate-qsum 50 --min-alternate-count 5 --min-alternate-fraction 0.2 {} > {}',
#                            [binaries['freebayes'], ref_fasta, abra_bam, vcf_freebayes]],

            'freebayes':['{} -f {} --standard-filters --report-genotype-likelihood-max --min-coverage 10 --min-alternate-qsum 50 --min-alternate-count 5 --min-alternate-fraction 0.2 {} > {}',
                            [binaries['freebayes'], ref_fasta, abra_bam, vcf_freebayes]],

            'deepvariant':['sudo docker run -v {}:/input -v {}:/output -v {}:/ref/ -v {}:/tmp/ google/deepvariant /opt/deepvariant/bin/run_deepvariant --model_type={} --ref=/ref/{} --reads=/input/{} --output_vcf=/output/{} --output_gvcf=/output/{} --intermediate_results_dir /tmp/intermediate_results_dir --num_shards={}',
                           [bam_dir, vcf_dir, ref_dir, tmp_dir, seq_mode, ref_basename, abra_bam.split('/')[-1], vcf_deepvariant, gvcf_deepvariant, threads]],

            'annovar_freebayes':['{}table_annovar.pl -thread {} -vcfinput {} {}humandb/ -buildver hg38 -out {}_freebayes -protocol gnomad41_exome,gnomad41_genome -operation f,f -nastring . -polish',
                       [annovar_dir, threads, vcf_freebayes, annovar_dir, annovar_vcf_mask]],

            'cravat_freebayes':['{} run {}_freebayes.hg38_multianno.vcf -l hg38 -t excel -a {} -d {} --mp {} -n {}_cravat_freebayes',
                      [binaries['cravat'], annovar_vcf_mask, cravat_annotators, annotation_dir, threads, basename]],

            'annovar_deepvariant':['{}table_annovar.pl -thread {} -vcfinput {} {}humandb/ -buildver hg38 -out {}_deepvariant -protocol gnomad41_exome,gnomad41_genome -operation f,f -nastring . -polish',
                       [annovar_dir, threads, vcf_deepvariant, annovar_dir, annovar_vcf_mask]],
            
            'cravat_deepvariant':['{} run {}_deepvariant.hg38_multianno.vcf -l hg38 -t excel -a {} -d {} --mp {} -n {}_cravat_deepvariant',
                      [binaries['cravat'], annovar_vcf_mask, cravat_annotators, annotation_dir, threads, basename]],

            'remove_tmp_files':['rm {}{}*',
                                [tmp_dir, basename]],
            }

    if module == 'all':
        return all_cmds
    
    cmd = {}
    if module == 'align':
        commands = ['trim_galore', 'trimmomatic', 'fastqc', 'aligning', 'samtools_sort', 'samtools_index', 'abra2', 'samtools_index_abra', 'remove_tmp_files']
    elif module == 'variant_calling':
        commands = ['freebayes']
        #commands = ['freebayes', 'deepvariant', 'remove_tmp_files']
    elif module == 'annotation':
        if 'freebayes' in sample:
            commands = ['annovar_freebayes', 'cravat_freebayes']
        elif 'deepvariant' in sample:
            commands = ['annovar_deepvariant', 'cravat_deepvariant']
    elif module == 'excel_postprocessing':
        commands = ['', '', '', '', '', '']
    for command in commands:
        cmd.update({command:all_cmds[command]})
    return cmd

def run_command(cmd: str, cmd_title: str, sample_name:str, check_run=False):
    stdout_file, stderr_file = open(log, 'a+'), open(errlog, 'a+')
    stdout_file.write(f'\n{sample_name}, {cmd_title}\n{cmd}'), stderr_file.write(f'\n{sample_name}, {cmd_title}\n{cmd}')
    stdout_file.close(), stderr_file.close()

    stdout_file, stderr_file = open(log, 'a+'), open(errlog, 'a+')
    result = subprocess.run(cmd, shell=True, encoding=encoding_os, stdout=stdout_file, stderr=stderr_file, check=check_run)
    stdout_file.close(), stderr_file.close()
    exit_code = result.returncode
    return exit_code

arg_descriptions = {'prolog':'pipeline v1',
                    'epilog':'(c) Kirill Baybekov',
                    'folder':'folder with fqs',
                    'threads':'threads to use',
                    'ref':'ref fasta',
                    'machine':'[medgen] Workmachine',
                    'sequence_mode':'[WES|WGS]',
                    'module':'''[all|trim|align|variant_calling|annotation|excel_postprocessing] Which module to run (default = "all"). Must be separated by comma.
                                all - full pipeline walkthrough, including fastq preparing, bam & vcf generating, variant annotation and excel postprocessing;
                                align - BAM generation with preprocessing fastqs by technical trimming and adapter removing. QC validation included;
                                variant_calling - VCF generation from BAM files
                                annotation - Generation of reports in XLSX format with using OpenCravat & hard_filtering script;
                                excel_postprocessing - Re-design of XLSX files to make it more usable''',
                    'exclude_samples':'Which samples to exclude from analysis. Must be separated by comma.',
                    'include_samples':'Which samples to include in analysis. Must be separated by comma.'}

parser = createParser()
namespace = parser.parse_args(sys.argv[1:])

threads = namespace.threads
machine = namespace.machine
seq_mode = namespace.mode
stages = namespace.module.split(',')
include = list_from_str(namespace.include_samples)
exclude = list_from_str(namespace.exclude_samples)
ref_fasta = namespace.ref
ref_basename = ref_fasta.split('/')[-1]
ref_dir = ref_fasta.replace(ref_basename, '')
dir = namespace.folder
res_dir, tmp_dir, bam_dir, vcf_dir, qc_dir, annotation_dir, excel_dir =  get_folders(dir)


stage_vars = {'align':[dir, bam_dir, '_R1.fastq.gz'],
              'variant_calling':[bam_dir,vcf_dir, '.bam'],
              'annotation':[vcf_dir, annotation_dir, '.vcf'],
              'excel_postprocessing':[annotation_dir, excel_dir, '.xlsx']}

cravat_annotators = 'clinvar clinvar_acmg omim ncbigene hpo hg19 gnomad spliceai cardioboost clinpred'
annovar_dir = '/mnt/d/WES/database/annovar/'

envs, binaries = get_env_list(machine)

encoding_os = os.device_encoding(1)
log = f'{res_dir}log.txt'
errlog = f'{res_dir}err_log.txt'

for module in stages:
    if module == 'align':
        os.system('export LC_ALL=en_US.UTF-8')
    run_pipeline(module=module, include_samples=include, exclude_samples=exclude)




'''r1s = [f'{dir}{file}' for file in os.listdir(dir) if file.endswith('R1.fastq.gz')]
for r1 in r1s:
    cmd, sample = generate_commands(r1)
    print(f'{sample}:')
    result = run_pipeline(cmd, sample)
    if result is not None:
        print('FINISHED ABNORMALLY')
        #exit(code=1)'''

#os.system(f'rm -rf {tmp_dir}')
'''multiqc_cmd = f'rename "s/_[1,2]P//" {qc_dir}* && {binaries["multiqc"]} {qc_dir} --outdir {qc_dir}multiqc/ --interactive'
run_command(multiqc_cmd, 'MultiQC', 'All samples')'''

'''time python3 /mnt/d/WES/pipeline_v2.py --machine medgen --threads 14 --mode WES --folder $WES/input/2024
0611_094557/Fastq/merged/ --ref $WES\/reference/Ensembl_hg38/Homo_sapiens.GRCh38.dna.primary_assembly.111.fa --module annotation --include_sa
mples 3147,4468,5938,5943,5985,5986,6102,6162,6455,6456,6457'''