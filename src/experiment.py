class Experiment:
    def __init__(self, date_from, date_to):
        self._date_from = date_from
        self._date_to = date_to
        self._results_by_day = []

    def check_for_absence(self):
        '''
        Check whether results contain all days and each day contains
        three corresponding resulted files: [ice, tracers, currents]
        :return:
        '''
        for day in self._results_by_day:
            print(day)

        pass


class ExperimentDay:
    def __init__(self, date, ice_file=None, tracers_file=None, currents_file=None):
        self.date = date
        self.ice_file = ice_file
        self.tracers_file = tracers_file
        self.currents_file = currents_file

    def __eq__(self, other):
        if isinstance(other, self.__class__):
            return self.date == other.date and self.ice_file == other.ice_file and \
                   self.tracers_file == other.tracers_file and \
                   self.currents_file == other.currents_file
        return False

    def __ne__(self, other):
        return self.date != other.date or self.ice_file != other.ice_file or \
               self.tracers_file != other.tracers_file or \
               self.currents_file != other.currents_file
