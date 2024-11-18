""" packages """
import enum


class MatchCriteriaEnum(enum.Enum):
    OnGuid = 1
    OnRelType = 2
    OnEntityType = 3


class LoggingLevelEnum(enum.Enum):
    NONE = 1
    SIMPLE = 2
    ADVANCED = 3
    FULL = 4
