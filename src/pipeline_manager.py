import os
import subprocess
from typing import List

class PipelineManager:
    def __init__(self, folder: str, threads: int, ref: str, place: str, mode: str, stages: List[str], include_samples: List[str], exclude_samples: List[str]):
        self.folder = folder
        self.threads = threads
        self.ref = ref
        self.place = place
        self.mode = mode
        self.stages = stages
        self.include_samples = include_samples
        self.exclude_samples = exclude_samples
        self.envs, self.binaries = self.get_env_list(place)
        self.res_dir, self.tmp_dir, self.bam_dir, self.vcf_dir, self.qc_dir, self.annotation_dir, self.excel_dir = self.get_folders(folder)
        self.stage_vars = {
            'align': [self.folder, self.bam_dir, '_R1.fastq.gz'],
            'variant_calling': [self.bam_dir, self.vcf_dir, '.bam'],
            'annotation': [self.vcf_dir, self.annotation_dir, '.vcf'],
            'excel_postprocessing': [self.annotation_dir, self.excel_dir, '.xlsx']
        }
        self.log = f'{self.res_dir}log.txt'
        self.errlog = f'{self.res_dir}err_log.txt'

    def get_folders(self, dir:str):
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

    def get_env_list(self, place: str):
        if place == 'igor':
            envs = {'samtools': 'genetico', 'freebayes': 'genetico', 'multiqc': 'genetico', 'cravat': 'cravat'}
            binaries = {
                'trim_galore': 'trim_galore',
                'trimmomatic': '/usr/share/java/trimmomatic-0.39.jar',
                'fastqc': 'fastqc',
                'samblaster': 'samblaster',
                'samtools': 'samtools',
                'abra2': '-Xmx48G -jar /root/miniforge3/envs/genetico/share/abra2-2.24-1/abra2.jar',
                'freebayes': 'freebayes',
                'multiqc': 'multiqc',
                'cravat': self.conda_run(envs['cravat'], 'oc')
            }
        else:
            envs = {'trim_galore': 'trim_galore', 'fastqc': 'fastqc'}
            binaries = {
                'trim_galore': self.conda_run(envs['trim_galore'], 'trim_galore'),
                'trimmomatic': '/home/medgen/programms/trimmomatic/trimmomatic-0.39.jar',
                'fastqc': self.conda_run(envs['fastqc'], 'fastqc'),
                'samblaster': '~/github/samblaster/samblaster',
                'samtools': 'samtools',
                'abra2': '-Xmx12G -jar ~/miniforge3/envs/abra2/share/abra2-2.24-3/abra2.jar',
                'freebayes': 'freebayes',
                'multiqc': 'multiqc'
            }
        return envs, binaries

    def conda_run(self, env, command):
        return f'conda run -n {env} {command}'

    def run_pipeline(self):
        for stage in self.stages:
            print(f'Running stage: {stage}')
            if stage == 'align':
                os.system('export LC_ALL=en_US.UTF-8')
            StageRunner(self).run_stage(stage)