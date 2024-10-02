import yaml
import os

def load_yaml(file_path, subsection=''):
    """
    Универсальная функция для загрузки данных из YAML-файла.
    
    :param file_path: Путь к YAML-файлу
    :param subsection: Этап пайплайна 
    :return: Словарь с данными из YAML-файла
    """
    with open(file_path, 'r') as file:
        if subsection == '':
            return yaml.safe_load(file)
        else:
            return yaml.safe_load(file)[subsection]
        
def save_yaml(filename, path, data):
    """
    Сохраняет словарь в файл в формате YAML.
    
    :param filename: Имя файла для сохранения (например, 'config.yaml')
    :param path: Путь к директории, где будет сохранён файл
    :param data: Словарь с данными, которые нужно сохранить в YAML
    """
    # Полный путь к файлу
    file_path = f'{path}{filename}.yaml'

    # Записываем данные в YAML-файл
    with open(file_path, 'w') as yaml_file:
        yaml.dump(data, yaml_file, default_flow_style=False)

def generate_cmd_data(args:dict,folders:dict, extension:str,
                      envs:dict, binaries:dict,
                      stage:str, log_dir:str):
    in_samples, ex_samples = args['include_samples'], args['exclude_samples']
    samples = generate_sample_list(in_samples, ex_samples, folders['input_dir'], extension)
    cmd_data = {}
    for sample in samples:
        commands = generate_commands(sample, stage, args, envs, binaries, folders)
        cmd_data.update({sample:commands})
    save_yaml('cmd_data', log_dir, cmd_data)
    return cmd_data

def generate_sample_list(in_samples:list, ex_samples:list,
                         input_dir:str, extension:str):
    
    samples = [s for s in os.listdir(input_dir) if s.endswith(extension)]
    if len(in_samples) != 0:
        samples =  [s for s in samples if any(inclusion in s for inclusion in in_samples)]
    if len(ex_samples) != 0:
        samples =  [s for s in samples if not any(exclusion in s for exclusion in ex_samples)]
    return [f'{input_dir}{s}' for s in samples]

def generate_commands(sample:str, stage:str,
                      envs:dict, binaries:dict,
                      folders:dict, args:dict):
    
    # Загружаем шаблоны файловых имён
    filenames_templates = load_yaml('config/filenames.yaml', stage)
    # Загружаем шаблоны команд
    cmd_templates = load_yaml('config/commands.yaml', stage)


    
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

    if stage == 'all':
        return all_cmds
    
    cmd = {}
    if stage == 'align':
        commands = ['trim_galore', 'trimmomatic', 'fastqc', 'aligning', 'samtools_sort', 'samtools_index', 'abra2', 'samtools_index_abra', 'remove_tmp_files']
    elif stage == 'variant_calling':
        commands = ['freebayes']
        #commands = ['freebayes', 'deepvariant', 'remove_tmp_files']
    elif stage == 'annotation':
        if 'freebayes' in sample:
            commands = ['annovar_freebayes', 'cravat_freebayes']
        elif 'deepvariant' in sample:
            commands = ['annovar_deepvariant', 'cravat_deepvariant']
    elif stage == 'excel_postprocessing':
        commands = ['', '', '', '', '', '']
    for command in commands:
        cmd.update({command:all_cmds[command]})
    return cmd