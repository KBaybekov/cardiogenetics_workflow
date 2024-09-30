class CommandExecutor:
    @staticmethod
    def run_command(cmd: str, cmd_title: str, sample_name: str):
        print(f'Running command: {cmd_title} for sample {sample_name}')
        result = subprocess.run(cmd, shell=True)
        return result.returncode