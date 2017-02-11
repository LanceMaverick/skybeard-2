'''
Equation Parser Module
----------------------

Parser for equations as strings which avoids using the 'unclean' method of eval() within python.

@author: Kristian Zarebski
@data: Last modified - 2017/02/11
'''
version = 'v0.1.0'

import logging
import sympy.mpmath as mt
from sympy import simplify
import re, sys

class EquationParser(object):
    '''Equation Parser Class'''

    def __init__(self, xarray):
        trig_dict = {'sin': mt.sin, 'cos': mt.cos, 'tan': mt.tan,
                     'asin': mt.asin, 'acos': mt.acos, 'atan': mt.tan,
                     'cosec': mt.csc, 'sec': mt.sec, 'cot': mt.cot,
                     'cospi': mt.cospi, 'sinpi': mt.sinpi, 'sinc': mt.sinc}
        hyp_dict = {'sinh': mt.sinh, 'cosh': mt.cosh, 'tanh': mt.tan,
                    'asinh': mt.asinh, 'acosh': mt.acosh, 'atanh': mt.tanh,
                    'cosech': mt.csch, 'sech': mt.sech, 'coth': mt.coth}

        log_ind_dict = {'log': mt.log, 'exp': mt.exp, 'log10': mt.log10}

        others_dict = {'sqrt': mt.sqrt, 'cbrt': mt.cbrt, 'root': mt.root,
                       'power': mt.power, 'expm1': mt.expm1,
                       'fac': mt.factorial, 'fac2': mt.fac2, 'gamma': mt.gamma,
                       'rgamma': mt.gamma, 'loggamma': mt.loggamma,
                       'superfac': mt.superfac, 'hyperfac': mt.hyperfac,
                       'barnesg': mt.barnesg, 'psi': mt.psi,
                       'harmonic': mt.harmonic}

        self._title = "\n=============WELCOME TO EQUATION PARSER {}=============\n".format(version)
        self.parser_dict = {}
        self.parser_dict.update(trig_dict)
        self.parser_dict.update(hyp_dict)
        self.parser_dict.update(log_ind_dict)
        self.parser_dict.update(others_dict)
        self.xarray = xarray
        self.user_marked_dict = {}
        self.eqn_string = ''
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(logging.ERROR)
        logging.basicConfig()
        self.eqn_string_template = ''
        self.eqn_string_id = ''
        self.accepted_opts = [')', '+', '-', '/', '*', '**']

    def clean_input(self, string):
        remainders = ''
        bad_chars = [';', '\\', '{', '}', '@', '$', '^', '&', 'rm', 'sudo', '~', '!', '#', ':', '|', '`', '\'', '"']
        for char in bad_chars:
            if char in string:
                remainders += char
        string = re.sub(r'\W+', '', string)
        string = re.sub(r'\d+', '', string)
        keys = [key for key in self.parser_dict]
        keys += 'x'
        for key in keys:
            string = string.replace(key, '')
        try:
          if len(list(remainders)) != 0:
               raise SystemExit()
          elif len(string) != 0:
               raise SyntaxError()
        except SystemExit:
            self.logger.critical("String contains Dangerous characters and will not be processed. Operation has terminated.")
            sys.exit(1) #HACK - Cannot get SystemExit to work properly
        except SyntaxError:
            self.logger.error("String contains unrecognised character combinations.")
            sys.exit()

    def set_logger_level(self, level):
        '''Set Level of output for Equation Parser Log'''
        if level == 'DEBUG':
            self.logger.setLevel(logging.DEBUG)
        elif level == 'INFO':
            self.logger.setLevel(logging.INFO)
        elif level == 'WARNING':
            self.logger.setLevel(logging.WARNING)
        elif level == 'CRITICAL':
            self.logger.setLevel(logging.CRITICAL)
        elif level == 'ERROR':
            self.logger.setLevel(logging.ERROR)
        else:
            self.logger.error("Invalid Logger Setting %s.", level)

    def apply_op(self, operation, val_str):
        '''Apply an operation to a value using parser operation dictionary'''
        self.logger.debug("Attempting to apply %s(%s)", operation, val_str)
        try:
            int(val_str)
        except ValueError:
            self.logger.error("Could not apply '%s' method to '%s'", operation, val_str)
        try:
            val = self.parser_dict[operation](float(val_str.replace('(', '').replace(')', '')))
            return '({})'.format(val)
        except KeyError:
            self.logger.error("Operation failed: Could not resolve %s(%s)", operation, val_str)

    def create_id_syntax(self, string=None):
        '''Create a string of digits to symbolize level of parenthesis'''
        if not string:
            string = self.eqn_string
        digi = 0
        self.logger.debug("Generating parenthesis level and marked equation strings.")
        for n_i, element in enumerate(string):
            if element == '(':
                self.eqn_string_template += '#'
                self.eqn_string_id += '{}'.format(digi+1)
                digi += 1
            elif self.eqn_string[n_i-1] == ')':
                digi -= 1
            self.eqn_string_template += element
            self.eqn_string_id += '{}'.format(digi+1)
        self.logger.debug("Level String '%s' generated.", self.eqn_string_id)
        self.logger.debug("Marked String '%s' generated", self.eqn_string_template)

    def create_parse_dictionary(self):
        '''Create Dictionary for Equation Layers'''
        self.user_marked_dict = {}
        self.logger.debug("Initialising New Equation Layers Dictionary.")

        for i, j in zip(self.eqn_string_id, self.eqn_string_template):
            try:
                if self.user_marked_dict[int(i)][-1] in self.accepted_opts or self.user_marked_dict[int(i)][-1] in self.parser_dict.keys():
                    self.user_marked_dict[int(i)] += '|'
                self.user_marked_dict[int(i)] += j
            except:
                self.user_marked_dict[int(i)] = j
        for key in self.user_marked_dict:
            for element in self.accepted_opts[1:]:
                self.user_marked_dict[key] = self.user_marked_dict[key].replace('{}|'.format(element),'{}'.format(element))
        self.logger.debug("Successfully created dictionary:\n %s", self.user_marked_dict)

    def recursive_split(self, string):
        init_string = string
        string = string.split('|')
        try:
            string = string[:-1] + string[-1].split('|')
        except:
            self.logger.debug("Successfully split string: %s", init_string)
        return string

    def evaluate_first_layer_val(self, value):
        keys = [key for key in self.user_marked_dict]
        maximum = max(keys)
        result = (self.user_marked_dict[maximum].replace('x', '{}'.format(value)))
        result = self.recursive_split(result)
        self.logger.debug("Using Sympy Simplify to parse %s", result)
        try:
            results = [str(simplify(r)) for r in result]
        except ValueError:
            self.logger.error("Could not evaluate strings %s", result)
            sys.exit()
        self.user_marked_dict[maximum] = results
        #if len(results) > 1:
        #    for r in results[1:]:
        #        self.user_marked_dict[maximum] += '|'
        #        self.user_marked_dict[maximum] += r
        self.logger.debug("Evaluating for value '%s'.", value)
        self.logger.debug("Innermost Layer set to '%s''", self.user_marked_dict)
        return maximum

    def evaluate_layer_i(self, k, value):
        output_string = ''
        n = 0
        prior_list = self.user_marked_dict[k+1]
        print(prior_list)
        current_list = list(self.user_marked_dict[k])
        for i in range(len(current_list)):
          if current_list[i] == '#':
              current_list[i] = current_list[i].replace('#', '({})'.format(prior_list[n]))
              n+=1
        for char in current_list:
            output_string += char
        output_string =  output_string.replace('x', '({})'.format(value))
        output_list = self.recursive_split(output_string)
        for i, element in enumerate(output_list):
            try:
                output_list[i] = simplify(element)
            except:
                continue
        self.logger.debug("Processed Layer %s: %s", k, output_list)
        self.user_marked_dict[k] = output_list

    def evaluate_val(self, value):
        max = self.evaluate_first_layer_val(value)
        self.logger.debug(self.user_marked_dict[1])
        self.evaluate_layer_i(max-1, value)
        self.evaluate_layer_i(max-2, value)

    def parse_equation_string(self, eqn_string):
        self.clean_input(eqn_string)
        '''Parse an equation which is of type string'''
        print(self._title)
        debug_title = '''
        -----------------------------------------
        EQUATION TO PARSE: {}
        X VALUES: 
        {}
        -----------------------------------------

        '''.format(eqn_string, self.xarray)

        self.logger.debug(debug_title)
        self.eqn_string = eqn_string
        self.create_id_syntax()
        self.create_parse_dictionary()
