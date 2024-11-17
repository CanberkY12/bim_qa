""" packages """
import json
import logging
""" modules """
from neo4jGraphDiff.Config.ConfiguratorEnums import MatchCriteriaEnum


class Configuration:
    """global configurator for everything related to the subgraph Diff in Neo4j"""

    def __init__(self, log_settings, diff_settings):
        """
        Constructor
        @param log_settings:
        @param diff_settings:
        """
        self.LogSettings = log_settings
        self.DiffSettings = diff_settings

    @classmethod
    def basic_config(cls):
        """
        Creates a default configuration without printing to console.
        @return: Config instance
        """
        logSettings = LoggingSettings.default_settings()
        diffSettings = DiffSettings()

        classObj = cls(logSettings, diffSettings)
        return classObj

    @classmethod
    def rel_type_config(cls):
        """
        Creates a default configuration without printing to console.
        @return: Config instance
        """
        logSettings = LoggingSettings.default_settings()
        diffSettings = DiffSettings()
        diffSettings.MatchingType_Childs = MatchCriteriaEnum.OnRelType

        classObj = cls(logSettings, diffSettings)
        return classObj

    @classmethod
    def entity_type_config(cls):
        """
        
        @return: Config instance
        """
        logSettings = LoggingSettings.default_settings()
        diffSettings = DiffSettings()
        diffSettings.MatchingType_Childs = MatchCriteriaEnum.OnEntityType

        classObj = cls(logSettings, diffSettings)
        return classObj

    @classmethod
    def on_guid_config(cls):
        """
        
        @return: Configuration
        """
        logSettings = LoggingSettings.default_settings()
        diffSettings = DiffSettings()
        diffSettings.MatchingType_RootedNodes = MatchCriteriaEnum.OnGuid
        diffSettings.MatchingType_Childs = MatchCriteriaEnum.OnRelType

        classObj = cls(logSettings, diffSettings)
        return classObj

    @classmethod
    def from_json(cls, jsonPath):
        """ loads the config from a specified json file and returns a Configuration instance """

        raise Warning('not implemented properly. Check ToDos')

        # ToDo: prepare everything to use this method with file-based jsons as well as HTTP request bodies
        # json import working for logsettings -- Benedict Harder
        with open(jsonPath) as f:
            json_obj = json.load(f)

        # snip the json
        try:
            logSettings_json = json_obj['loggingSettings']
            diffSettings_json = json_obj['diffSettings']
        except:
            raise Exception('Staged an invalid config file. please check. ')

        ## create class instances
        # logSettings = LoggingSettings.from_json(logSettings_json)
        # diffSettings = DiffSettings.from_json(diffSettings_json)

        return cls(logSettings, diffSettings)

    def to_json(self):
        """ writes the current config to a json """
        pass

    # dunder
    def __repr__(self):
        return 'Config: matchingType_rootedNodes: {} matchingType_components: {}'.format(
            self.DiffSettings.MatchingType_RootedNodes, self.DiffSettings.MatchingType_Childs)


class LoggingSettings:
    def __init__(self, to_console, to_file, log_file_path, log_formatter, log_console_level, log_file_level):
        self.logToConsole = to_console
        self.logToFile = to_file
        self.logFilePath = log_file_path
        self.logFormatter = log_formatter
        self.logConsoleLevel = log_console_level
        self.logFileLevel = log_file_level

    @classmethod
    def default_settings(cls):
        return cls(False, True, 'myapp.log', logging.Formatter('%(asctime)s: %(name)s: %(message)s'), logging.INFO, logging.INFO)

    @classmethod
    def from_json(cls, obj):
        """ generate instance from JSON """
        bool_file = obj['logToFile']
        bool_console = obj['logToConsole']
        logPath = obj['loggingFilePath']
        # Format
        if obj['loggingFormat'] == "standard":
            logFormat = logging.Formatter('%(asctime)s: %(name)s: %(message)s')
        else:
            raise Exception('Invalid value in defaultConfig.json')
        # Console Level
        if obj['loggingLevelConsole'] == "simple":
            levelConsole = logging.INFO
        else:
            raise Exception('Invalid value in defaultConfig.json')
        # File Level
        if obj['loggingLevelFile'] =="simple":
            levelFile = logging.INFO
        else:
            raise Exception('Invalid value in defaultConfig.json')
        # ToDo: Implement cast to LoggingLevelEnum
        return cls(bool_console, bool_file, logPath, logFormat, levelConsole, levelFile)

    def to_json(self):
        """ write instance to JSON """
        raise Exception('This method is not implemented yet')

    def initialize_logger(self, logger):
        """ initialize a logger with settings from the class"""
        logger.setLevel(logging.DEBUG)

        # config for logging to a file
        if self.logToFile:
            file_handler = logging.FileHandler(self.logFilePath, mode = 'a')
            file_handler.setLevel(self.logFileLevel)
            file_handler.setFormatter(self.logFormatter)
            logger.addHandler(file_handler)

        # config for logging to console
        if self.logToConsole:
            stream_handler = logging.StreamHandler()
            stream_handler.setFormatter(self.logFormatter)
            stream_handler.setLevel(self.logConsoleLevel)
            logger.addHandler(stream_handler)

        return logger

    # --- dunder ---
    def __repr__(self):
        return 'LoggingSettings: ToConsole: {}, ToFile: {}, ConsoleLevel: {}, FileLevel: {}'.format(self.logToConsole, self.logToFile, self.logConsoleLevel, self.logFileLevel)

    def __str__(self):
        return 'LoggingSettings: ToConsole: {}, ToFile: {}, ConsoleLevel: {}, FileLevel: {}'.format(self.logToConsole, self.logToFile, self.logConsoleLevel, self.logFileLevel)


class DiffSettings:
    """ """

    def __init__(self):
        # ignore settings
        self.diffIgnoreAttrs = ["p21_id", "GlobalId"]
        self.diffIgnoreEntityTypes = []
        self.MatchingType_RootedNodes = MatchCriteriaEnum.OnGuid  # sets how rooted nodes get matched
        self.MatchingType_Childs = MatchCriteriaEnum.OnRelType  # sets how child nodes get matched

    @classmethod
    def defaultSettings(cls):
        return cls()

    @classmethod
    def from_json(cls, obj):
        """ generate instance from JSON """
        raise Exception('This method is not implemented yet')

    def ToJson(self):
        """ write instance to JSON """
        raise Exception('This method is not implemented yet')

    # --- dunder ---
    def __repr__(self):
        return 'DiffSettings: IgnoreAttrs: {} IgnoreEntityTypes: {}'.format(self.diffIgnoreAttrs,
                                                                            self.diffIgnoreEntityTypes)

    def __str__(self):
        return 'DiffSettings: IgnoreAttrs: {} IgnoreEntityTypes: {}'.format(self.diffIgnoreAttrs,
                                                                            self.diffIgnoreEntityTypes)
