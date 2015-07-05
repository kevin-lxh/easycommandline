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
```
```
$ python favcolor.py -r -w
    - red
    - white
```

# Coercion
```python
# file demo.py

import sys
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
program.parse(sys.argv)

print 'recursive  : ', program.recursive
print 'preload    : ', program.preload
print 'name       : ', program.name
print 'integer    : ', program.integer
print 'float      : ', program.float
print 'collection : ', program.collection
print 'range      : ', program.range
print 'sum        : ', program.sum
```
```
$ python demo.py -p --name Tracy -i 1000 --range 5..8 -s 1 2 3 4
    recursive  :  None
    preload    :  True
    name       :  Tracy
    integer    :  1000
    float      :  None
    collection :  []
    range      :  [5, 6, 7]
    sum        :  10
```

# Automated --help
```
$ python demo.py -h

    Usage: python demo.py [options]

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
