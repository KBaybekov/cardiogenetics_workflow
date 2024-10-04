import subprocess

class CommandExecutor:
    @staticmethod
    def run_command(cmd: str, cmd_title: str, sample_name: str):
        print(f'Running command: {cmd_title} for sample {sample_name}')
        result = subprocess.run(cmd, shell=True)
        return result.returncode
    


            for sample in c.keys():
            for cmd_name, (command, args) in c[sample].items():
                shell_command = command.format(*args)
                result = CommandExecutor.run_command(shell_command, cmd_name, sample)
                if result != 0:
                    print(f'ERROR: {cmd_name} failed on {sample}, exit code: {result}')
                    return result
        return 0