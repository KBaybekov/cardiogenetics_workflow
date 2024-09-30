from utils import *
import os
from typing import List

class PipelineManager:
    def __init__(self, args):
        """
        Конструктор, принимающий аргументы командной строки и инициализирующий параметры пайплайна.
        """
        # Извлекаем параметры из args
        self.input_dir = args.input_dir
        self.output_dir = args.output_dir
        self.threads = args.threads
        self.ref = args.ref
        self.place = args.place
        self.mode = args.mode
        self.stages = args.stage
        self.include_samples = args.include_samples
        self.exclude_samples = args.exclude_samples
        self.filter_common_variants = args.filter_common_variants
        self.variant_frequency_threshold = args.variant_frequency_threshold

        # Инициализируем окружения и бинарные файлы
        self.envs, self.binaries = self.get_env_list(self.place)

        # Загружаем переменные для стадий
        for stage in self.stages:
            stage_vars = load_yaml('config/stage_vars.yaml')[stage]
            #ДОДЕЛАТЬ

        # Создаём директории для результатов
        self.folders = self.get_folders(self.input_dir, self.output_dir)
        self.res_dir, self.tmp_dir, self.bam_dir, self.vcf_dir, self.qc_dir, self.annotation_dir, self.excel_dir = self.get_folders(self.folder)

        # Лог файлы
        self.log_dir = os.path.join(self.res_dir, 'Logs')
        os.makedirs(self.log_dir, exist_ok=True)
        self.log = f'{self.log_dir}/log.txt'
        self.errlog = f'{self.log_dir}/err_log.txt'
        
        # Логи
        self.log_dir = os.path.join(self.res_dir, 'Logs')
        os.makedirs(self.log_dir, exist_ok=True)
        self.log = os.path.join(self.log_dir, 'log.yaml')
        self.errlog = os.path.join(self.log_dir, 'err_log.yaml')

        # Сохраняем все начальные параметры в лог
        self.save_to_log('init_config', self.__dict__)

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

    def get_env_list(self, place):
        # Загружаем окружения и бинарные файлы из envs.yaml
        env_config = load_yaml('config/envs.yaml')[place]
        envs = env_config['envs']
        binaries = env_config['binaries']
        return envs, binaries

    def conda_run(self, env, command):
        return f'conda run -n {env} {command}'

    def run_pipeline(self):
        for stage in self.stages:
            print(f'Running stage: {stage}')
            if stage == 'align':
                os.system('export LC_ALL=en_US.UTF-8')
            StageRunner(self).run_stage(stage)