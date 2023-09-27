import logging


class FilterLevels(logging.Filter):
    """
    Check Filter levels and record level of logs.
    """
    def __init__(self, filter_levels=None):
        super(FilterLevels, self).__init__()
        self._filter_levels = filter_levels

    def filter(self, record):
        """
        Check record level name should be filter level name
        """
        return record.levelname in self._filter_levels
