from datetime import datetime
from utils import run_command, load_yaml, update_yaml


class CommandExecutor:
    def __init__(self, cmd_data:dict, log_space:dict, module:str):
        self.cmd_data = cmd_data
        self.log = log_space['log_data']
        self.stdout = log_space['stdout_log']
        self.stderr = log_space['stderr_log']
        self.module = module
        self.module_start_time = datetime.now().strftime("%d.%m.%Y_%H:%M:%S")

    def execute(self, samples:list):
        cmds:dict
        cmds = self.cmd_data[sample]
        self.result = load_yaml(file_path=self.log)
        self.result.update({f'{self.module}_{self.module_start_time}':{}})
        # Алиас
        m = self.result[f'{self.module}_{self.module_start_time}']
        for sample in samples:
            print(f'Sample: {sample}')
            sample_result = {}
            for title, cmd in cmds.items():
                print(f'\t{title}:', end='')
                sample_result[title] = run_command(cmd=cmd, cmd_title=title)
                r = sample_result[title]
                if r['status'] == 'FAIL':
                    print(f'FAIL, exit code: {r["exit_code"]}. ', end='')
                else:
                    print(f'OK. ', end='')
                print(f'Duration: {r['duration']}')
                m.update({sample:sample_result})
                update_yaml(file_path=self.log, new_data=m)