class Neo4jFactory:

    def __init__(self):
        pass

    @classmethod
    def BuildMultiStatement(cls, cypherCMDs):
        """
        constructs a multi-statement cypher command
        @param cypherCMDs:
        @return:
        """
        return ' '.join(cypherCMDs)

    @classmethod
    def formatDict(cls, dictionary):
        """
        formats a given dictionary to be understood in a cypher query
        @param dictionary: dict to be formatted
        @return: string representation of dict
        """
        s = "{"

        for key in dictionary:
            s += "{0}:".format(key)
            if isinstance(dictionary[key], dict):
                # Apply formatting recursively
                s += "{0}, ".format(dictionary(dictionary[key]))
            elif isinstance(dictionary[key], list):
                s += "["
                for l in dictionary[key]:
                    if isinstance(l, dict):
                        s += "{0}, ".format(dictionary(l))
                    else:
                        # print(l)
                        if isinstance(l, int):
                            s += "{0}, ".format(l)
                        else:
                            s += "'{0}', ".format(l)
                if len(s) > 1:
                    s = s[0: -2]
                s += "], "
            else:
                if isinstance(dictionary[key], (int, float)):
                    s += "{0}, ".format(dictionary[key])
                else:
                    s += "\"{0}\", ".format(dictionary[key])
        # Quote all the values
        # s += "\'{0}\', ".format(self[key])

        if len(s) > 1:
            s = s[0: -2]
        s += "}"
        return s
