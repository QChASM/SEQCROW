from SEQCROW.managers import QMInputManager

from inspect import signature


class ConformerSearch(QMInputManager):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
