import sys
import re


class Option(object):
    def __init__(self, info): # params (symbol, fullname, description, action, initial_arg)
        if isinstance(info, (list, tuple)) == False or len(info) < 2:
            raise Exception('option name missing')

        self.symbol = info[0]

        self.fullname = info[1].strip()
        name_components = self.fullname.split(' ')
        self.name = name_components[0]

        if not Option.is_valid_symbol(self.symbol):
            raise Exception('`({0}, {1}, ...)` is invalid, the symbol must start with `-`, such as `-f`'.format(self.symbol, self.fullname))

        if not Option.is_valid_name(self.name):
            raise Exception('`({0}, {1}, ...)` is invalid, the option name must start with `--`, such as `--foo`'.format(self.symbol, self.fullname))

        self.description = info[2] if len(info) >= 3 else ''
        self.action = info[3] if len(info) >= 4 else None

        self.initial_arg_set = len(info) >= 5
        self.initial_arg = info[4] if self.initial_arg_set else None

        self.arg_required = self.action is not None


    @classmethod
    def is_valid_symbol(cls, text):
        return (re.match(r'^-[a-zA-Z]$', text) is not None)


    @classmethod
    def is_valid_name(cls, text):
        return (re.match(r'^--[a-zA-Z]', text) is not None)




class OptionParser(object):
    def __init__(self, options, argv):
        self.__options = options[:];
        self.__argv = argv[:]
        self.__argv.pop(0)


    def parse(self):
        start_index = 0

        name_to_argument_mapping = {}
        for option in self.__options:
            name_to_argument_mapping[option.name] = option.initial_arg

        while True:
            location, length = self.__range_for_option_and_argv(start_index)

            if length == 0: # done
                break

            symbol_or_name = self.__argv[location]
            option = self.__find_option_by_symbol_or_name(symbol_or_name)
            argv_for_option = self.__argv[(location+1) : (location+length)]

            argument = self.__parse_for_an_option(option, argv_for_option)
            name_to_argument_mapping[option.name] = argument

            start_index = location + length

        return name_to_argument_mapping


    def __parse_for_an_option(self, option, argv):
        a_single_argument = option.initial_arg

        if len(argv) == 0:
            if option.arg_required:
                raise Exception('option `{0}, {1}` argument missing'.format(option.symbol, option.fullname))
            else:
                a_single_argument = True

        else:
            if option.action:
                if option.initial_arg_set: # reduce
                    for arg in argv:
                        previous_value = a_single_argument
                        a_single_argument = option.action(arg, previous_value)

                else: # call action with first argument
                    a_single_argument = option.action(argv[0])

            else:
                a_single_argument = argv[0]

        return a_single_argument


    def __range_for_option_and_argv(self, start_index):
        location = None
        length = 0

        for index in range(start_index, len(self.__argv)):
            text = self.__argv[index]

            is_option_symbol_or_name = ( Option.is_valid_symbol(text[:2]) or Option.is_valid_name(text) )
            if is_option_symbol_or_name:
                if self.__find_option_by_symbol_or_name(text) is None:
                    raise Exception("unknown option `{0}`".format(text))
                
            if is_option_symbol_or_name:
                if location is None:
                    location = index
                    length = 1
                else:
                    break # done

            else: # an argument
                if location is not None:
                    length += 1

        return (location, length)


    def __find_option_by_symbol_or_name(self, symbol_or_name):
        for option in self.__options:
            if option.symbol == symbol_or_name or option.name == symbol_or_name:
                return option

        return None
    



class Commander(object):
    def __init__(self):
        self.__script_name = None
        self.__version = '1.0.1'

        self.__options = []
        self.__name_to_argument_mapping = {}

        self.__max_length_of_name = 0
        self.__max_length_of_description = 0

        self.options(
            ('-h', '--help', 'output usage information'),
            ('-V', '--version', 'output the version number'),
            )

        self.arguments = None

        
    def version(self, version):
        self.__version = version


    def options(self, *options):
        for option_info in options:
            try:
                option = Option(option_info)
            except Exception, e:
                self.__print_exception(e)
                sys.exit()

            self.__append_option(option)


    def __append_option(self, option):
        self.__options.append(option)

        self.__name_to_argument_mapping[option.name] = option.initial_arg

        self.__max_length_of_name = max(len(option.fullname), self.__max_length_of_name)
        self.__max_length_of_description = max(len(option.description), self.__max_length_of_description)


    def parse(self, argv):
        self.__script_name = argv[0]
        try:
            self.__name_to_argument_mapping = OptionParser(self.__options, argv).parse()    
        except Exception, e:
            self.__print_exception(e)
            sys.exit()
        
        self.__did_parse_options()


    def __did_parse_options(self):
        if self.arg('help'):
            self.__print_help()
            sys.exit()

        if self.arg('version'):
            self.__print_version()
            sys.exit()

        for option_name in self.__name_to_argument_mapping:
            attr = option_name[2:]
            setattr(self, attr, self.__name_to_argument_mapping[option_name])
            

    def arg(self, attr_name):
        key = '--' + attr_name
        return self.__name_to_argument_mapping.get(key)


    def __print_help(self):
        print('\n  Usage: python {0} [options]'.format(self.__script_name))
        print('\n  Options:\n')

        for option in self.__options:
            text = '  {0}, {1:{width1}}  {2:{width2}}'.format(
                option.symbol, option.fullname, option.description,
                width1=self.__max_length_of_name, width2=self.__max_length_of_description)
            print(text)

        print('')


    def __print_version(self):
        print(self.__version)


    def __print_exception(self, e):
        print('\n  error: {0}\n'.format(e))




program = eval('Commander()') # eval, avoid methods checking to `program`
