from uuid import uuid4
import equatic
import re

class TelePlot:
    def __init__(self, eqn_string, options, debug='INFO'):
        self.eqn_string = eqn_string
        self.options = options
        self.xlabel = 'x'
        self.ylabel = 'f(x)'
        self.title = None
        self.loglevel = debug
        self.plot_opts = '-'
        self.line_styles = {'—' : '--', 'dashed' : '--', '-.' : '-.',
                            'dotdash' : '.-', ':' : ':', 'dotted' : ':',
                            'none' : ''}
        self.colors = {'blue' : 'b', 'green' : 'g', 'red' : 'r', 'cyan' : 'c',
                            'magenta' : 'm', 'yellow' : 'y', 'black' : 'k',
                            'white' : 'w', 'b' : 'b', 'g' : 'g', 'r' : 'r',
                            'm' : 'm', 'y' : 'y', 'k' : 'k', 'w' : 'w'}

        self.marker_styles = {'.' : '.', 'point' : '.', ',' : ',',
                              'pixel' : ',', 'o' : 'o', 'circle' : 'o',
                              'v' : 'v', 'dtriangle' : 'v',
                              '^' : '^', 'triangle' : '^',
                              '<' : '<', 'ltriangle' : '<',
                              '>' : '>', 'rtriangle' : '>',
                              '8' : '8', 'octagon' : '8',
                              's' : 's', 'square' : 's',
                              'p' : 'p', 'pentagon' : 'p',
                              '*' : '*', 'star' : '*',
                              'h' : 'h', 'hexagon' : 'h',
                              'x' : 'x', '+' : '+', 'plus' : '+',
                              'D' : 'D', 'diamond' : 'D', 
                              'd' : 'd', 'diamond2' : 'd',
                              '|' : '|', 'vline' : '|',
                              '_' : '_', 'hline' : '_',
                              'tickleft' : 'TICKLEFT',
                              'tickright' : 'TICKRIGHT',
                              'tickup' : 'TICKUP',
                              'tickdown' : 'TICKDOWN',
                              'caretleft' : 'CARETLEFT',
                              'caretright' : 'CARETRIGHT',
                              'caretup' : 'CARETUP',
                              'caretdown' : 'CARETDOWN'}
        self.func_range = self.parse_opts()


    def parse_opts(self):
        n = 1000
        range_ = [0.1, 10]
        for opts_tuple in self.options:
            if 'title' in opts_tuple[0]:
                self.title = r'{}'.format(opts_tuple[1])
            if 'marker' in opts_tuple[0]:
                self.plot_opts += self.marker_styles[opts_tuple[1]]
            if 'color' in opts_tuple[0]:
                self.plot_opts += self.colors[opts_tuple[1]]
            if 'linestyle' in opts_tuple[0]:
                self.plot_opts = self.plot_opts.replace('-', self.line_styles[opts_tuple[1]])
            if 'options' in opts_tuple[0]:
                self.plot_opts = opts_tuple[1]
            if 'xlabel' in opts_tuple[0]:
                print("Got Axis title for x of " + opts_tuple[1])
                self.xlabel = r'{}'.format(opts_tuple[1])
            if 'ylabel' in opts_tuple[0]:
                self.ylabel = r'{}'.format(opts_tuple[1])
            if 'range' in opts_tuple[0]:
                numbers = re.findall('([\d\.\-]+)', opts_tuple[1])
                range_ = [float(i) for i in numbers]
                if len(range_) < 3:
                  range_.append(n)
                range_[2] = int(range_[2])
        return range_

    def save_plot(self):
        filename = './{}.png'.format(str(uuid4())[:6])
        print(self.plot_opts)
        equatic.plot(self.eqn_string, self.func_range, ylabel=self.ylabel, 
                    xlabel=self.xlabel, save=filename, plot_opts=self.plot_opts, 
                    debug=self.loglevel, show=False, title=self.title)
        return filename

