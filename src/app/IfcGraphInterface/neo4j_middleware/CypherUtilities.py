
class CypherUtilities:

    @classmethod
    def parse_attrs(cls, all_attributes_raw: list) -> dict:
        """
        translates attributes extracted with regex into full python dicts
        @param all_attributes_raw:
        @return:
        """
        attr_dict = {}
        for t in all_attributes_raw:
            # t is a tuple
            attr_name = t[0]
            attr_val = t[1]

            # polish attr name
            attr_name = attr_name.replace("'", "").replace(" ", "")

            # polish attr value
            attr_val: str = attr_val.replace(" ", "")

            # cast to boolean
            if attr_val.upper() == "TRUE" or attr_val.upper() == "FALSE":
                evaluated_val = bool(attr_val)

            # cast to any other datatype supported in python
            else:
                evaluated_val = eval(attr_val)

            # add to dictionary
            attr_dict[attr_name] = evaluated_val

        return attr_dict
