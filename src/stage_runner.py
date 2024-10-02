from utils import *
from pipeline_manager import PipelineManager
from command_executor import CommandExecutor

class StageRunner:
    def __init__(self, pipeline_manager: PipelineManager):
        self.pipeline_manager = pipeline_manager
        
    def run_stage(self, stage: str):
        x = self.pipeline_manager

        cmd_data = generate_cmd_data(in_samples=x.args['include_samples'], ex_samples=x.args['exclude_samples'],
                                     folders=x.folders, extension=x.extensions[stage], envs=x.envs,
                                     binaries=x.binaries, stage=stage, log_dir=x.log_dir)
        for sample in cmd_data.keys():
            for cmd_name, (command, args) in cmd_data[sample].items():
                shell_command = command.format(*args)
                result = CommandExecutor.run_command(shell_command, cmd_name, sample)
                if result != 0:
                    print(f'ERROR: {cmd_name} failed on {sample}, exit code: {result}')
                    return result
        return 0
    