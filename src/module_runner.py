from utils import *
from pipeline_manager import PipelineManager
from command_executor import CommandExecutor

class ModuleRunner:
    def __init__(self, pipeline_manager: PipelineManager):
        self.pipeline_manager = pipeline_manager
        
    def run_stage(self, module: str):
        print(f'Running module: {module}')

        x = self.pipeline_manager
        # Создаём директории для результатов
        for path in x.folders[module].values():
            os.makedirs(path, exist_ok=True)
        
        cmd_data = generate_cmd_data(args=x.args, folders=x.folders,
                                     extension=x.extensions[module], envs=x.envs,
                                     binaries=x.binaries, module=module,
                                     log_dir=x.log_dir)
        for sample in cmd_data.keys():
            for cmd_name, (command, args) in cmd_data[sample].items():
                shell_command = command.format(*args)
                result = CommandExecutor.run_command(shell_command, cmd_name, sample)
                if result != 0:
                    print(f'ERROR: {cmd_name} failed on {sample}, exit code: {result}')
                    return result
        return 0
    