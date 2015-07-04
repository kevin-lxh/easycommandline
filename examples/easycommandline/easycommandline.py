import sys

class Option(object):
    def __init__(self, option): # arg => (symbol, fullname, description, action, initial_arg)
        if isinstance(option, (list, tuple)) == False or len(option) < 2:
            raise Exception('option name missing')

        self.symbol = option[0]

        self.fullname = option[1].strip()
        name_components = self.fullname.split(' ')
        self.name = name_components[0]
        
        self.description = option[2] if len(option) >= 3 else ''
        self.action = option[3] if len(option) >= 4 else None

        self.initial_arg_set = len(option) >= 5
        self.arg = option[4] if self.initial_arg_set else None

        self.arg_required = self.action is not None
        

class Commander(object):
    def __init__(self):
        self.__script_name = None
        self.__version = '1.0.1'

        self.__options = []
        self.__symbol_to_option_mapping = {}
        self.__name_to_option_mapping = {}

        self.__max_length_of_name = 0
        self.__max_length_of_description = 0

        help = Option(['-h', '--help', 'output usage information'])
        help.arg_required = False
        self.__append_option(help)

        version = Option(['-V', '--version', 'output the version number'])
        version.arg_required = False
        self.__append_option(version)


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

        self.__symbol_to_option_mapping[option.symbol] = option
        self.__name_to_option_mapping[option.name] = option

        self.__max_length_of_name = max(len(option.fullname), self.__max_length_of_name)
        self.__max_length_of_description = max(len(option.description), self.__max_length_of_description)


    def parse(self, argv):
        self.__argv = argv[:]
        self.__script_name = self.__argv.pop(0)

        start_index = 0
        while True:
            try:
                location, length = self.range_for_option(start_index)
            except Exception, e:
                self.__print_exception(e)
                sys.exit()

            if length == 0: # done
                break

            # find option
            symbol_or_name = self.__argv[location]
            option = self.__symbol_to_option_mapping.get(symbol_or_name)
            if option is None:
                option = self.__name_to_option_mapping.get(symbol_or_name)

            # option.arg
            arguments = self.__argv[location+1 : location+length]
            if len(arguments) == 0:
                if option.arg_required:
                    self.__print_exception('option `{0}, {1}` argument missing'.format(option.symbol, option.fullname))
                    sys.exit()
                else:
                    option.arg = True

            else:
                if option.action:
                    if option.initial_arg_set: # reduce
                        for value in arguments:
                            option.arg = option.action(value, option.arg)

                    else: # call action with first argument
                        option.arg = option.action(arguments[0])

                else:
                    option.arg = arguments[0]

            # start_index
            start_index = location + length

        self.__did_parse_argv()


    def __did_parse_argv(self):
        if self.arg('help'):
            self.__print_help()
            sys.exit()

        if self.arg('version'):
            self.__print_version()
            sys.exit()
            

    def arg(self, option_name):
        option_name = '--' + option_name
        option = self.__name_to_option_mapping.get(option_name)
        if option:
            return option.arg
        else:
            return None


    def range_for_option(self, start_index):
        option_start_index = 0
        option_length = 0

        for index in range(start_index, len(self.__argv)):
            text = self.__argv[index]

            is_option_prefix = False

            # symbol
            if text[:2] == '--' and len(text) != 2:
                if self.__name_to_option_mapping.get(text) is not None:
                    is_option_prefix = True
                else:
                    raise Exception("unknown option `{0}`".format(text))

            elif text[:1] == '-' and len(text) != 1 and text != '--':
                if self.__symbol_to_option_mapping.get(text) is not None:
                    is_option_prefix = True
                else:
                    raise Exception("unknown option `{0}`".format(text))                    

            # index
            if is_option_prefix:
                if option_length == 0:
                    option_start_index = index
                    option_length = 1
                else:
                    break

            else: 
                if option_length > 0:
                    option_length += 1

        return (option_start_index, option_length)


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


program = Commander()
arg = program.arg