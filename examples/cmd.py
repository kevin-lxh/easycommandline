from easycommandline import program
import os

program.version('1.0.1')


cmd = program.cmd('cd <path>')
cmd.options(
    ('-c', '--create', 'create directory if not existed'),
    )
cmd.description('change directory')
@cmd.action
def action_for_cmd_cd(cmd, path):
    if cmd.create and not os.path.exists(path):
        os.makedirs(path)



cmd = program.cmd('start server <path> [env]')
@cmd.action
def action_for_cmd_start_server(cmd, path, env):
    print(path)
    print(env)


program.parse_argv()
