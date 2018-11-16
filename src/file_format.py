import logging
import os
import re

import yaml


class FileFormat:
    def __init__(self, format_file="../formats/nemo14-formats.yaml"):
        self.format_file = format_file
        self._formats = self.load_formats()
        self._vars_formats = self.init_vars_formats()

    def load_formats(self):
        with open(os.path.join(os.path.dirname(__file__), self.format_file), 'r') as stream:
            try:
                loaded = yaml.load(stream)
                return loaded
            except yaml.YAMLError as exc:
                print(exc)
                logging.info(exc)

    def init_vars_formats(self):
        vars_by_type = {}
        types = [type for type in self._formats['files']]

        for type in types:
            vars_by_type[type] = []
            for var in self._formats['files'][type]['vars']:
                vars_by_type[type].append(Variable(var['name'], var['shape']))

        return vars_by_type

    def match_type(self, name):
        for type in self._formats['files'].keys():
            _, error = self.match(name, type)
            if error is "":
                return type, ""

        error = "%s has no matching type" % name

        return "", error

    def match(self, name, type):
        '''

        :param name: name of NetCDF-file
        :param type: type of simulation result: ice, tracers or currents
        :return: extracted date as string if name matches for pattern
        '''

        pattern = self._formats['files'][type]['name']
        date = ""
        error = ""
        try:
            matches = re.search(pattern, name).groups()
            # TODO: assertion error for wrf-files
            # assert matches[0] == matches[1]
            if type == 'waves':
                if len(matches) != 2:
                    raise Exception
                year, month = matches
                return (int(year), int(month)), ''
            else:

                if len(matches) > 1 and matches[1] != '' and matches[0] != matches[1]:
                    raise Exception
                date = matches[0]

        except Exception:
            error = "%s doesn't correspond to name format of %s" % (name, type)

        return date, error

    def format(self, date, type):
        return str.join("", [self._formats['files'][type]['prefix'], date.strftime(self._formats['date']),
                             "-", date.strftime(self._formats['date']), self._formats['files'][type]['suffix']])

    def variables(self, type):
        '''

        :param type: ice, tracers, currents
        :return: List of oceanic variables that must be presented in simulation result-file of a given type
        '''

        return self._vars_formats[type]

    def leap_years(self):
        return self._formats['leap_years']


class Variable:
    def __init__(self, name, shape):
        self.name = name
        self.shape = shape

    def match(self, var, *args, **kwargs):
        var_shape = list(var.shape)

        is_error = False

        # Dirty hack with wrf leap years
        if 'wrf' in kwargs:

            if len(self.shape) != len(var_shape) or self.shape[1:] != var_shape[1:]:
                is_error = True
            else:
                if len(self.shape) > 2:
                    year = kwargs['year']
                    file_format = kwargs['file_format']
                    time_idx = 0
                    if (self._is_leap(year, file_format) and self.shape[time_idx] < 8784) or \
                            (not self._is_leap(year, file_format) and self.shape[time_idx] < 8760):
                        log_prefix = " ".join(args)

                        shape_to_print = self.shape
                        shape_to_print[time_idx] = 8784 if self._is_leap(year, file_format) else 8760
                        print(year, shape_to_print, var_shape)
                        return f"{log_prefix} Variable: {self.name} doesn't correspond to pattern, expected: " \
                               f"{shape_to_print}, actual: {str(var_shape)}"

        else:
            if len(self.shape) != len(var_shape) or self.shape != var_shape:
                is_error = True

        if is_error:
            log_prefix = " ".join(args)
            return f"{log_prefix} Variable: {self.name} doesn't correspond to pattern, expected: " \
                   f"{self.shape}, actual: {str(var_shape)}"

        return ""

    def _is_leap(self, year, file_format):
        return True if year in file_format.leap_years() else False
