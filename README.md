# easycommandline.py
a solution for python command-line interfaces, inspired by [tj/commander.js](https://github.com/tj/commander.js)

# Installation
```
$ pip install easycommandline
```

# Option
Options are defined with the `.options()` method, also serving as documentation for the options. The example below parses args and options from `sys.argv`
```python
# file favcolor.py

from easycommandline import program

program.version('1.0.1')
program.options(
        ('-r', '--red'),
        ('-g', '--green'),
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
```
```
$ python favcolor.py -r -w
    - red
    - white
```

# Coercion
```python
# file coercion.py

from easycommandline import program

def collect(value, previous_value):
    previous_value.append(value)
    return previous_value

def make_range(value):
    components = value.split('..')
    return range( int(components[0]), int(components[1]) )

def sum(value, previous_value):
    return previous_value + int(value)

program.version('1.0.1')
program.options(
        ('-r', '--recursive'),
        ('-p', '--preload', 'preload enabled'),
        ('-n', '--name', 'username'),
        ('-i', '--integer <int>', 'an integer argument', int),
        ('-f', '--float <float>', 'a float argument', float),
        ('-a', '--anotherfloat', 'another float argument', float),
        ('-c', '--collection [example]', 'collection', collect, []),
        ('-x', '--range A..B', 'range', make_range),
        ('-s', '--sum', 'the sum of numbers', sum, 0),
    )
program.parse_argv()

print('recursive  : ', program.recursive)
print('preload    : ', program.preload)
print('name       : ', program.name)
print('integer    : ', program.integer)
print('float      : ', program.float)
print('collection : ', program.collection)
print('range      : ', program.range)
print('sum        : ', program.sum)
```
```
$ python coercion.py -p --name Tracy -i 1000 --range 5..8 -s 1 2 3 4
    recursive  :  None
    preload    :  True
    name       :  Tracy
    integer    :  1000
    float      :  None
    collection :  []
    range      :  [5, 6, 7]
    sum        :  10
```

# Command
specify argument required with `< >`  
specify argument optional with `[ ]`, can not specify more than one optional argument
```python
# file cmd.py

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

```
```
$ python cmd.py cd ~/Desktop/abc -c
$ python cmd.py start server ~/Desktop/abc production
```

# Automated --help
```
$ python coercion.py -h

    Usage: python coercion.py [options]

    Options:

    -h, --help                  output usage information 
    -V, --version               output the version number
    -r, --recursive                                      
    -p, --preload               preload enabled          
    -n, --name                  username                 
    -i, --integer <int>         an integer argument      
    -f, --float <float>         a float argument         
    -a, --anotherfloat          another float argument   
    -c, --collection [example]  collection               
    -x, --range A..B            range                    
    -s, --sum                   the sum of numbers      
```
