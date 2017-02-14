from uuid import uuid4
import equatic

class TelePlot:
    def __init__(self, eqn_string, options):
        self.eqn_string = eqn_string
        self.options = options
        self.xlabel = 'x'
        self.ylabel = 'f(x)'
        self.func_range = self.parse_opts()

    def parse_opts(self):
        n = 1000
        range_ = [0.1, 10]
        for opts_tuple in self.options:
            if 'xlabel' in opts_tuple[0]:
                print("Got Axis title for x of " + opts_tuple[1])
                self.xlabel = opts_tuple[1]
            if 'ylabel' in opts_tuple[0]:
                self.ylabel = opts_tuple[1]
            if 'range' in opts_tuple[0]:
                numbers = opts_tuple[1].split(',')
                range_ = numbers
                if len(range_) > 2:
                    n = (float(range_[1]) - float(range_[0])) / int(range_[2])
        range_.append(n)
        return range_

    def save_plot(self):
        filename = './{}.png'.format(str(uuid4())[:6])
        equatic.plot(self.eqn_string, self.func_range, ylabel=self.ylabel, xlabel=self.xlabel, save=filename)
        return filename
