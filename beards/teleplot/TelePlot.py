import matplotlib.pyplot as plt
from uuid import uuid4
import mpmath as mt
import re
import numpy as np

trig_dict = {'sin': mt.sin, 'cos': mt.cos, 'tan': mt.tan,
             'asin': mt.asin, 'acos': mt.acos, 'atan': mt.tan,
             'cosec': mt.csc, 'sec': mt.sec, 'cot': mt.cot,
             'cospi': mt.cospi, 'sinpi': mt.sinpi, 'sinc': mt.sinc}
hyp_dict = {'sinh': mt.sinh, 'cosh': mt.cosh, 'tanh': mt.tan,
            'asinh': mt.asinh, 'acosh': mt.acosh, 'atanh': mt.tanh,
            'cosech': mt.csch, 'sech': mt.sech, 'coth': mt.coth}

logInd_dict = {'log': mt.log, 'exp': mt.exp, 'log10': mt.log10}

others_dict = {'sqrt': mt.sqrt, 'cbrt': mt.cbrt, 'root': mt.root,
               'power': mt.power, 'expm1': mt.expm1,
               'fac': mt.factorial, 'fac2': mt.fac2, 'gamma': mt.gamma,
               'rgamma': mt.gamma, 'loggamma': mt.loggamma,
               'superfac': mt.superfac, 'hyperfac': mt.hyperfac,
               'barnesg': mt.barnesg, 'psi': mt.psi,
               'harmonic': mt.harmonic}

eqn_parser = {}
eqn_parser.update(trig_dict)
eqn_parser.update(hyp_dict)
eqn_parser.update(logInd_dict)
eqn_parser.update(others_dict)


def checkandParse(string):
    opts2perform = {}
    for key in eqn_parser:
        regex_str = '({})\(([xy\+\-\/\*\.\d]+)\)'.format(key)
        res = re.findall(regex_str, string)
        if len(res) > 0:
            opts2perform[key] = res[0]
    return opts2perform


class TelePlot:
    def __init__(self, plot_type='scatter', style='default'):
        self.plotType = plot_type
        self.plotStyle = style
        self.xlabel = 'x'
        self.ylabel = 'y'
        self.x = []
        self.y = []

    def parseOpts(self, in_array):
        n = 100
        range_ = [-10, 10]
        for opts_tuple in in_array:
            if 'xaxis' in opts_tuple[0]:
                print("Got Axis title for x of " + opts_tuple[1])
                self.xlabel = opts_tuple[1]
            if 'yaxis' in opts_tuple[0]:
                self.ylabel = opts_tuple[1]
            if 'range' in opts_tuple[0]:
                numbers = opts_tuple[1].split(',')
                range_ = numbers
                if len(range_) > 2:
                    n = (float(range_[1]) - float(range_[0])) / int(range_[2])
        self.x = np.linspace(float(range_[0]), float(range_[1]), n)

    def savePlot(self):
        plt.xlabel(self.xlabel)
        plt.ylabel(self.ylabel)
        print(self.y)
        plt.plot(self.x, self.y)
        filename = './{}.png'.format(str(uuid4())[:6])
        plt.savefig(filename)
        plt.clf()
        return filename
