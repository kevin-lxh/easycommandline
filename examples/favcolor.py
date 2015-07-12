from easycommandline import program

program.version('1.0.1')
program.options(
    ('-r', '--red'),
    ('-b', '--blue'),
    ('-w', '--white'),
    )
program.parse_argv()

if program.red:
    print('- red')
if program.blue:
    print('- blue')
if program.white:
    print('- white')