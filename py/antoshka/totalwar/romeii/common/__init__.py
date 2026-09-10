from enum import StrEnum as _StrEnum, auto


class StrEnum(_StrEnum):
    @staticmethod
    def _generate_next_value_(name, start, count, last_values):
        return name