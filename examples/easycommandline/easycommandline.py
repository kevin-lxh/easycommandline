import sys
import re

class Option(object):
    def __init__(self, option): # params (symbol, fullname, description, action, initial_arg)
        if isinstance(option, (list, tuple)) == False or len(option) < 2:
            raise Exception('option name missing')

        self.symbol = option[0]

        self.fullname = option[1].strip()
        name_components = self.fullname.split(' ')
        self.name = name_components[0]


        if not Option.is_valid_symbol(self.symbol):
            raise Exception('`({0}, {1}, ...)` is invalid, the symbol must start with `-`, such as `-f`'.format(self.symbol, self.fullname))

        if not Option.is_valid_name(self.name):
            raise Exception('`({0}, {1}, ...)` is invalid, the option name must start with `--`, such as `--foo`'.format(self.symbol, self.fullname))

        self.description = option[2] if len(option) >= 3 else ''
        self.action = option[3] if len(option) >= 4 else None

        self.initial_arg_set = len(option) >= 5
        self.initial_arg = option[4] if self.initial_arg_set else None

        self.arg_required = self.action is not None


    @classmethod
    def is_valid_symbol(cls, text):
        return (re.match(r'^-[a-zA-Z]', text) is not None)


    @classmethod
    def is_valid_name(cls, text):
        return (re.match(r'^--[a-zA-Z]', text) is not None)


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
        for a_list in options:
            try:
                option = Option(a_list)
            except Exception, e:
                self.__print_exception(e)
                sys.exit()

            self.__append_option(option)


    def __append_option(self, option):
        self.__options.append(option)

        self.__name_to_argument_mapping[option.name] = option.initial_arg

        self.__max_length_of_name = max(len(option.fullname), self.__max_length_of_name)
        self.__max_length_of_description = max(len(option.description), self.__max_length_of_description)


    def __find_option_by_symbol_or_name(self, symbol_or_name):
        for option in self.__options:
            if option.symbol == symbol_or_name or option.name == symbol_or_name:
                return option

        return None


    def parse(self, argv):
        argv = argv[:]
        self.__script_name = argv.pop(0)

        start_index = 0
        while True:
            try:
                location, length = self.__range_for_option(start_index, argv)
            except Exception, e:
                self.__print_exception(e)
                sys.exit()

            if length == 0: # done
                break

            # find option
            symbol_or_name = argv[location]
            option = self.__find_option_by_symbol_or_name(symbol_or_name)

            # parse argv
            arguments_for_option = argv[(location+1) : (location+length)]
            if len(arguments_for_option) == 0:
                if option.arg_required:
                    self.__print_exception('option `{0}, {1}` argument missing'.format(option.symbol, option.fullname))
                    sys.exit()
                else:
                    self.__name_to_argument_mapping[option.name] = True

            else:
                if option.action:
                    if option.initial_arg_set: # reduce
                        for value in arguments_for_option:
                            previous_value = self.__name_to_argument_mapping[option.name]
                            new_value = option.action(value, previous_value)
                            self.__name_to_argument_mapping[option.name] = new_value

                    else: # call action with first argument
                        value = option.action(arguments_for_option[0])
                        self.__name_to_argument_mapping[option.name] = value

                else:
                    value = arguments_for_option[0]
                    self.__name_to_argument_mapping[option.name] = arguments_for_option[0]

            # start_index
            start_index = location + length

        self.__did_parse_argv()           


    def __range_for_option(self, start_index, argv):
        location = None
        length = 0

        for index in range(start_index, len(argv)):
            text = argv[index]

            is_option = False
            if Option.is_valid_symbol(text) or Option.is_valid_name(text):
                if self.__find_option_by_symbol_or_name(text):
                    is_option = True
                else:
                    raise Exception("unknown option `{0}`".format(text))
                
            # location, length
            if is_option:
                if location is None:
                    location = index
                    length = 1
                else:
                    break

            else: 
                if location is not None:
                    length += 1

        return (location, length)
    

    def __did_parse_argv(self):
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
        return self.__name_to_argument_mapping[key]


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


program = eval('Commander()') # eval, avoid from methods checking for `program`
