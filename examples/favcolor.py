import sys
from easycommandline import program

program.version('1.0.1')
program.options(
    ('-r', '--red'),
    ('-g', '--green'),
    ('-b', '--blue'),
    ('-w', '--white'),
    )
program.parse(sys.argv)

if program.red:
    print('- red')
if program.blue:
    print('- blue')
if program.white:
    print('- white')