import sys
import os
import re
import terminalstyle as style
import inspect


class DevelopmentException(Exception):
    def __init__(self, message):
        message = style.red(message)
        super(DevelopmentException, self).__init__(message)


class UsageException(Exception):
    def __init__(self, message):
        super(UsageException, self).__init__(message)





class Option(object):
    def __init__(self, *info): # params => (symbol, fullname, description, action, initial_val)
        if len(info) < 2:
            raise DevelopmentException('option name missing')

        self.symbol = info[0]
        self.fullname = info[1].strip()
        self.name = self.fullname.split(' ')[0]

        symbol_is_valid = (self.is_option_symbol(self.symbol) and len(self.symbol) == 2)
        symbol_is_empty = len(self.symbol) == 0
        if not symbol_is_valid and not symbol_is_empty:
            error = '`({0}, {1}, ...)` option error, the symbol should be a two-character string starts with `-`, such as `-f`'.format(self.symbol, self.fullname)
            raise DevelopmentException(error)

        if not self.is_option_name(self.name):
            error = '`({0}, {1}, ...)` option error, the option name should be a string starts with `--`, such as `--foo`'.format(self.symbol, self.fullname)
            raise DevelopmentException(error)

        self.description = info[2] if len(info) >= 3 else ''
        self.action = info[3] if len(info) >= 4 else None

        self.initial_val_set = len(info) >= 5
        self.initial_val = info[4] if self.initial_val_set else None

        self.arg_required = self.action is not None


    @classmethod
    def is_option_symbol(cls, text):
        return re.match('^-[a-zA-Z]+', text) is not None


    @classmethod
    def is_option_name(cls, text):
        return re.match('^--[a-zA-Z]+', text) is not None





class OptionParser(object):
    def __init__(self, options, raw_args):
        self.__options = options[:];
        self.__raw_args = raw_args[:]


    def parse(self, force_to_bool=False):
        option_to_argument_mapping = {}

        for option in self.__options:
            if force_to_bool:
                option_to_argument_mapping[option] = False
            else:
                option_to_argument_mapping[option] = option.initial_val

        raw_option_to_args_mapping = self.__raw_option_to_args_mapping()
        for raw_option in raw_option_to_args_mapping:
            option = self.__find_option_by_symbol_or_name(raw_option)
            if option is None:
                raise UsageException('unknown option `{0}`'.format(raw_option))

            if force_to_bool:
                option_to_argument_mapping[option] = True
            else:
                args = raw_option_to_args_mapping[raw_option]
                a_single_argument = self.__reduce_args(option, args)
                option_to_argument_mapping[option] = a_single_argument

        return option_to_argument_mapping


    def __raw_option_to_args_mapping(self):
        raw_option_to_args_mapping = {}

        ranges = self.__ranges_of_raw_option_and_args()
        for (location, length) in ranges:
            option_symbol_or_name = self.__raw_args[location]
            args_for_option = self.__raw_args[(location+1) : (location+length)]

            if Option.is_option_symbol(option_symbol_or_name):
                text = option_symbol_or_name
                multiple_symbols_taken = len(text) > 2
                if multiple_symbols_taken:
                    for char in list(text[1:]): # list(text[1:]), for example, convert '-rxq' to ['r', 'x', 'q']
                        if char == '-':
                            continue

                        symbol = '-' + char
                        raw_option_to_args_mapping[symbol] = []

                    continue

            raw_option_to_args_mapping[option_symbol_or_name] = args_for_option

        return raw_option_to_args_mapping


    def __ranges_of_raw_option_and_args(self):
        ranges = []

        location = None
        length = 0

        for index in range(len(self.__raw_args)):
            text = self.__raw_args[index]

            is_option_symbol_or_name = Option.is_option_symbol(text) or Option.is_option_name(text)

            if is_option_symbol_or_name:
                if location is not None:
                    ranges.append([location, length])

                location = index
                length = 1

            else: # an argument
                length += 1

        if location is not None:
            ranges.append([location, length])

        return ranges


    def __reduce_args(self, option, args):
        a_single_argument = option.initial_val

        if len(args) == 0:
            if option.arg_required:
                error = 'option `{0}, {1}` argument missing'.format(option.symbol, option.fullname)
                raise UsageException(error)
            else:
                a_single_argument = True

        else:
            if option.action:
                if option.initial_val_set:
                    for arg in args:
                        previous_value = a_single_argument
                        a_single_argument = self.__invoke_option_action(option.action, arg, previous_value)

                else: # call action with first arg
                    a_single_argument = self.__invoke_option_action(option.action, args[0])

            else:
                a_single_argument = args[0]

        return a_single_argument


    def __find_option_by_symbol_or_name(self, symbol_or_name):
        for option in self.__options:
            if option.symbol == symbol_or_name or option.name == symbol_or_name:
                return option

        return None


    def __invoke_option_action(self, action, *args):
        spec = inspect.getargspec(action)
        if len(spec.args) != len(args):
            error = 'option action `{0}()` takes {1} arguments ({2} declared)'.format(action.__name__, len(args), len(spec.args))
            raise DevelopmentException(error)

        return action(*args)






class CommandComponent(object):
    TYPE_CMD_NAME = 0
    TYPE_OPTIONS = 1
    TYPE_ARG_REQUIRED = 2
    TYPE_ARG_OPTIONAL = 3

    def __init__(self, a_type, value):
        self.type = a_type
        self.value = value        






class Command(object):

    def __init__(self, format):
        self.__format = format
        self.__components = self.__components_for_format()

        self.__description = ''
        self.__options = []
        self.__actions = []


    def options(self, *option_info_group):
        for info in option_info_group:
            if type(info) != tuple and type(info) != list:
                error = 'command `{0}`, argument of options() should be a tuple or list'.format(self.__format)
                raise DevelopmentException(error)

            option = Option(*info)
            self.__options.append(option)


    def action(self, action):
        self.__actions.append(action)
        return None


    def description(self, description):
        self.__description = description


    def perform(self, raw_args):
        # matching
        matcher = self.__matcher()
        raw_args_str = ' '.join(raw_args)

        match = re.match(matcher, raw_args_str)
        if match is None:
            return False

        # parse options
        force_to_bool = self.__is_arguments_specified()
        option_to_argument_mapping = OptionParser(self.__options, raw_args).parse(force_to_bool)

        for option in option_to_argument_mapping:
            attr = option.name[2:]
            argument = option_to_argument_mapping[option]
            setattr(self, attr, argument)

        # perform action
        if len(self.__actions) > 0:
            args = self.__extract_args_for_action(raw_args)
            self.__trigger_actions(args)

        return True


    def details(self):
        name = []
        args = []
        for c in self.__components:
            if c.type == c.TYPE_CMD_NAME:
                name.append(c.value)
            elif c.type == c.TYPE_ARG_REQUIRED or c.type == c.TYPE_ARG_OPTIONAL:
                args.append(c.value)
        
        name = ' '.join(name)
        args = ' '.join(args)

        return (name, args, self.__description[:], self.__options[:], self.__components[:])


    def __components_for_format(self):
        components = []

        elements = re.split('\s+(?!([^<]*>|[^\[]*\]))', self.__format)
        args_start_index = None

        for ele in elements:
            if ele is None or len(ele) == 0:
                continue

            start = ele[0]
            end = ele[-1]

            if start == '<' and end == '>':
                component = CommandComponent(CommandComponent.TYPE_ARG_REQUIRED, ele)
                components.append(component)
                if args_start_index is None:
                    args_start_index = len(components) - 1

            elif start == '[' and end == ']':
                component = CommandComponent(CommandComponent.TYPE_ARG_OPTIONAL, ele)
                components.append(component)
                if args_start_index is None:
                    args_start_index = len(components) - 1

            elif Option.is_option_symbol(ele) or Option.is_option_name(ele):
                component = CommandComponent(CommandComponent.TYPE_OPTIONS, ele)
                components.append(component)
            
            else:
                component = CommandComponent(CommandComponent.TYPE_CMD_NAME, ele)
                components.append(component)

        # validate
        self.__validate_components(components)
            
        return components


    def __validate_components(self, components):
        number_of_args_optional = 0
        number_of_args = 0

        for c in components:
            if c.type == c.TYPE_ARG_REQUIRED:
                number_of_args += 1
                if number_of_args_optional > 0:
                    error = 'cmd(\'{0}\') format error, optional argument should be the last argument'.format(self.__format)
                    raise DevelopmentException(error)

            elif c.type == c.TYPE_ARG_OPTIONAL:
                number_of_args += 1
                number_of_args_optional += 1
                if number_of_args_optional > 1:
                    error = 'cmd(\'{0}\') format error, command can only receive one optional argument'.format(self.__format)
                    raise DevelopmentException(error)

            elif c.type == c.TYPE_OPTIONS:
                error = 'cmd(\'{0}\') format error, should not specify options `{1}` in command format, use cmd.options()'.format(self.__format, c.value)
                raise DevelopmentException(error)                

            elif c.type == c.TYPE_CMD_NAME:
                if number_of_args > 0:
                    error = 'cmd(\'{0}\') format error, command name should be in front of any argument'.format(self.__format)
                    raise DevelopmentException(error)


    def __matcher(self):
        regxes = []
        for c in self.__components:
            if c.type == c.TYPE_CMD_NAME:
                escaped_text = re.sub(r'[\.\$\^\{\[\(\|\)\*\+\?\\]', (lambda m : '\\'+m.group()), c.value)
                regxes.append(escaped_text + '(\s+|$)')

        return '^' + ''.join(regxes)


    def __extract_args_for_action(self, raw_args):
        if self.__is_arguments_specified() == False:
            return [self]

        args = raw_args[:]

        # remove command name
        for c in self.__components:
            if c.type == c.TYPE_CMD_NAME:
                args.pop(0)
            else:
                break

        # remove options
        indexes = range(len(args))
        indexes.reverse()
        for i in indexes:
            arg = args[i]
            if Option.is_option_symbol(arg) or Option.is_option_name(arg):
                args.pop(i)

        return [self] + args


    def __is_arguments_specified(self):
        for c in self.__components:
            if c.type == c.TYPE_ARG_REQUIRED or c.type == c.TYPE_ARG_OPTIONAL:
                return True

        return False


    def __trigger_actions(self, args):
        for action in self.__actions:
            spec = inspect.getargspec(action)
            if spec.varargs is None:
                diff = len(spec.args) - len(args)
                if diff > 0:
                    for i in range(diff):
                        args.append(None)

                action(*args[0:len(spec.args)])
            else:
                action(*args)






class Program(object):
    HELP_OPTION_INFO = ('-h', '--help', 'output usage information')
    VERSION_OPTION_INFO = ('-V', '--version', 'output the version number')

    def __init__(self):
        self.__script_name = ''
        self.__version = ''

        self.__cmds = []
        self.__builtin_cmd = self.__setup_buildin_cmd()
        

    def version(self, version):
        self.__version = version


    def options(self, *option_info_group):
        self.__builtin_cmd.options(*option_info_group)


    def cmd(self, cmd_format):
        if cmd_format.strip() == '' and len(self.__cmds) > 0:
            return self.__builtin_cmd

        cmd = Command(cmd_format)
        cmd.options(self.HELP_OPTION_INFO)
        @cmd.action
        def action(cmd, *args):
            if cmd.help:
                self.print_help(cmd)
                sys.exit()

        self.__cmds.append(cmd)
        return cmd


    def parse_argv(self):
        self.__script_name = os.path.basename(sys.argv[0])
        raw_args = sys.argv[1:]

        try:
            for cmd in self.__sorted_cmds():
                if cmd.perform(raw_args):
                    return

        except UsageException, e:
            print('\n  Error: {0}\n'.format(e))
            sys.exit()


    def print_help(self, cmd):
        # print options
        cmd_name, cmd_args, description, options, components = cmd.details()

        print('')
        cmd_name_width = len(cmd_name) + 2 if len(cmd_name) > 0 else 1
        print('  Usage: {0}{1:^{width}}[options] {2}'.format(self.__script_name, cmd_name, cmd_args, width=cmd_name_width))
        print('')
        print(style.bold('  Options:'))

        max_length_of_option_name = 0
        for option in options:
            max_length_of_option_name = max(len(option.fullname), max_length_of_option_name)

        for option in options:
            text = '  {0:4}{1:{width}}  {2}'.format(
                (option.symbol + ',') if option.symbol else '',
                option.fullname,
                option.description,
                width=max_length_of_option_name)
            print(text)

        print('')

        # print commands
        if cmd != self.__builtin_cmd or len(self.__cmds) == 1:
            return

        print(style.bold('  Commands:'))
            
        max_length_of_cmd_name = 0
        for cmd in self.__cmds:
            cmd_name, cmd_args, description, options, components = cmd.details()
            max_length_of_cmd_name = max(len(cmd_name), max_length_of_cmd_name)

        for cmd in self.__cmds:
            cmd_name, cmd_args, description, options, components = cmd.details()
            if cmd == self.__builtin_cmd:
                continue

            text = '  {0:{width}}   {1}'.format(
                    cmd_name,
                    description,
                    width=max_length_of_cmd_name
                )
            print(text)

        print('')


    def __setup_buildin_cmd(self):
        cmd = self.cmd('')
        cmd.options(self.VERSION_OPTION_INFO)
        @cmd.action
        def action(cmd, *args):
            if cmd.version:
                print self.__version
                sys.exit()

            name, args, description, options, components = cmd.details()
            for option in options:
                attr = option.name[2:]
                argument = getattr(cmd, attr)
                setattr(self, attr, argument)

        return cmd


    def __sorted_cmds(self):
        def key(cmd):
            cmd_name, cmd_args, description, options, components = cmd.details()
            return len(cmd_name)

        return sorted(self.__cmds, key=key, reverse=True)





program = eval('Program()') # eval, avoid methods checking to `program`


