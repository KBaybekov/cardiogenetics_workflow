class StageRunner:
    def __init__(self, pipeline_manager: PipelineManager):
        self.pipeline_manager = pipeline_manager

    def run_stage(self, stage: str):
        cmd_data = self.pipeline_manager.generate_cmd_data(stage)
        for sample in cmd_data.keys():
            for cmd_name, (command, args) in cmd_data[sample].items():
                shell_command = command.format(*args)
                result = CommandExecutor.run_command(shell_command, cmd_name, sample)
                if result != 0:
                    print(f'ERROR: {cmd_name} failed on {sample}, exit code: {result}')
                    return result
        return 0