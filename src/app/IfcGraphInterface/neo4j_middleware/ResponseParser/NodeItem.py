from typing import List

import neo4j.data
import neo4j.graph

from neo4j_middleware.CypherUtilities import CypherUtilities
from neo4j_middleware.Neo4jFactory import Neo4jFactory
import re


class NodeItem:
    """
    reflects the node structure from neo4j
    """

    def __init__(self, node_id: int, rel_type: str = None):
        """
        @param node_id: node id in the graph database
        @param rel_type: rel_type of edge pointing to this node
        """
        self.id: int = node_id
        self.rel_type = rel_type
        self.attrs = None
        self.labels = []
        self.node_identifier = ""

    def __hash__(self):
        return hash((self.id, self.rel_type, *self.attrs, *self.labels, self.node_identifier))

    def get_entity_type(self) -> str:
        """
        returns the entityType label of the node
        """
        return self.attrs.get("EntityType", None)

    def get_timestamps(self) -> list:
        """
        returns the attached timestamp labels of the given node
        """
        ts = [x for x in self.labels if x.startswith('ts')]
        return ts

    def get_listitem(self) -> int:
        if 'listItem' in self.rel_type:
            return int(self.rel_type["listItem"])
        else:
            return -1

    def get_node_type(self) -> str:
        """
        returns the node type label (either primary, secondary, or connectionNode).
        returns "VirtualNode" in case of a non-existent (i.e., -1) node
        """
        try:
            node_type = [x for x in self.labels if not x.startswith('ts') and not x.startswith('Ifc')][0]
        except:
            node_type = "VirtualNode"
        return node_type

    def get_node_identifier(self):
        if self.node_identifier == "":
            return "n{}".format(self.id)
        else:
            return self.node_identifier

    # ToDo: consider implementing python properties for managed access

    def __repr__(self):
        return 'NodeItem: id: {} var: {} attrs: {} labels: {}' \
            .format(self.id, self.node_identifier, self.attrs, self.labels)

    def __eq__(self, other):
        """
        implements a comparison function. matching by node id
        @param other:
        @return:
        """
        if self.id == other.id:
            return True
        else:
            return False
        # ToDo: eq comparison is not valid for cypher-based DPO

    @classmethod
    def from_neo4j_response_with_rel(cls, raw: str) -> list:
        ret_val = []
        for inst in raw:
            node_type = inst[4][0]
            # child = cls(node_id=int(inst[0]), rel_type=inst[1]['rel_type'], entity_type=inst[2])
            child = cls(node_id=int(inst[0]), rel_type=inst[1]['rel_type'])
            child.labels.append(node_type)
            if 'listItem' in inst[1]:
                child.rel_type = inst[1]['rel_type'] + '__listItem{}'.format(inst[1]['listItem'])
                # ToDo: consider to re-model the recursive Diff approach by incorporating edgeItems
            attrs = inst[3]
            child.attrs = attrs
            ret_val.append(child)
        return ret_val

    @classmethod
    def from_neo4j_response_wou_rel(cls, raw: str) -> list:
        """
        expects a list of records
        requires the following statements inside the RETURN:
        ID(n), n.EntityType, PROPERTIES(n), LABELS(n)
        """
        ret_val = []
        for inst in raw:
            node_labels = list(inst[3])
            node_type = [x for x in node_labels if not x.startswith('ts')][0]
            child = cls(node_id=int(inst[0]), rel_type=None)
            child.labels.append(node_type)
            attrs = inst[2]
            child.attrs = attrs
            ret_val.append(child)
        return ret_val

    @classmethod
    def from_neo4j_response(cls, raw) -> list:
        """
        creates a List of NodeItem instances from a given neo4j response
        @param raw: neo4j response string
        @return:
        """

        # allocate return value
        ret_val = []

        # prevent case of empty raw input
        if raw == []:
            return []

        if type(raw) == list:

            # cast
            for raw_node in raw:

                # unpack if record
                if type(raw_node) == neo4j.data.Record:
                    raw_node = raw_node[0]

                node_labels = list(raw_node.labels)
                node = cls(node_id=int(raw_node.id), rel_type=None)
                node.set_node_attributes(dict(raw_node._properties))
                node.labels = node_labels
                ret_val.append(node)

            return ret_val

        if type(raw) == neo4j.data.Record:
            # passed a single node into the method, therefore we can skip the unpacking

            # cast
            for raw_node in raw:
                node_labels = list(raw_node.labels)
                node = cls(node_id=int(raw_node.id), rel_type=None)
                node.set_node_attributes(dict(raw_node._properties))
                node.labels = node_labels
                ret_val.append(node)

        elif type(raw) == neo4j.graph.Node:
            raw_node = raw
            node_labels = list(raw_node.labels)
            node = cls(node_id=int(raw_node.id), rel_type=None)
            node.set_node_attributes(dict(raw_node._properties))
            node.labels = node_labels
            ret_val.append(node)

        return ret_val

    @classmethod
    def from_cypher_fragment(cls, raw: str):

        # pre-processing
        if raw[-1] != "}":
            raw += ":{}"

        # regex definitions
        reg_attr_extractor = r"\{([^]]+)\}"
        reg_attr_separator = r"(.+?):(.+?),"
        reg_node_var = r"^(.+?)(:|^)"
        reg_node_labels = r":([^]]+)\{"

        # information to be extracted using regex
        node_var = ""
        labels = ""
        attributes = ""

        # get variable def in current cypher query (unique to each query)
        node_var = re.findall(reg_node_var, raw)[0][0]

        # get node labels
        node_label_raw = re.findall(reg_node_labels, raw)
        if len(node_label_raw) != 0:
            labels = node_label_raw[0].replace(" ", "").split(":")
            if '' in labels:
                labels.remove('')

        # get attributes
        attributes_raw = re.findall(reg_attr_extractor, raw)
        if len(attributes_raw) != 0:
            attributes = attributes_raw[0] + ", "

        # get attributes with regex
        all_attributes_raw = re.findall(reg_attr_separator, attributes)
        # cast attributes to python dict
        attr_dict = CypherUtilities.parse_attrs(all_attributes_raw)

        # init new node item
        node = cls(node_id=0)
        node.attrs = attr_dict
        node.labels = labels
        node.node_identifier = node_var

        # return newly created nodeItem
        return node

    def set_node_attributes(self, attrs):
        """
        assigns attributes to node item
        @param attrs: dict or list
        @return: nothing
        """
        if isinstance(attrs, list):
            d = attrs[0]
            self.attrs = d
        else:
            self.attrs = attrs

    def tidy_attrs(self, remove_None_values: bool = True):
        """
        removes entity_type and p21_id from attr dict
        @return:
        """

        if self.id == -1:
            # virtual node, nothing to clean
            return

        # self.attrs.pop("EntityType", None)
        self.attrs.pop("p21_id", None)
        self.attrs.pop('rel_type', None)

        if remove_None_values is True:
            # remove attrs that have a none value assigned
            cleared_dict = {}
            for key, val in self.attrs.items():
                if val != 'None':
                    cleared_dict[key] = val
                if key in ['Coordinates', 'DirectionRatios']:
                    cleared_dict[key] = eval(val)
            self.attrs = cleared_dict

    def to_cypher(self, skip_attributes: bool = False, skip_labels: bool = False, entType_guid_only: bool = False):
        """
        returns a cypher query fragment to search for or to create this node with semantics
        @param skip_labels:
        @param skip_attributes:
        @type entType_guid_only: returns a reduced attr definition for patternmatching
        @return:
        """

        if self.id == -1:
            # virtual node
            return '()'
        if "p21_id" in self.attrs:
            cy_node_identifier = "n" + str(self.attrs["p21_id"])
        else:
            cy_node_identifier = self.get_node_identifier()

        cy_node_attrs = ""
        cy_node_labels = ""

        if skip_attributes is False:
            if self.attrs != {}:
                if entType_guid_only:
                    # remove all attributes except GUID and EntityType
                    reduced_attrs = {"EntityType": self.attrs["EntityType"]}
                    if "GlobalId" in self.attrs:
                        reduced_attrs["GlobalId"] = self.attrs["GlobalId"]

                    # send reduced dict to factory
                    cy_node_attrs = Neo4jFactory.formatDict(reduced_attrs)

                else:
                    cy_node_attrs = Neo4jFactory.formatDict(self.attrs)

        if skip_labels is False:
            if len(self.labels) > 0:
                for label in self.labels:
                    cy_node_labels += ":{}".format(label)

        # remove p21_id attribute
        cleaned_node_attrs = self.attrs
        # cleaned_node_attrs.pop('p21_id', None)

        return '({0}{1}{2})'.format(cy_node_identifier, cy_node_labels, cy_node_attrs)

    def to_arrows_vis(self, ignore_null_values: bool = False, x_pos = 0, y_pos = 0, create_relaxed_pattern: bool=False):
        """
        prepares a node to be visualized in the arrows app
        @param ignore_null_values:
        @param x_pos:
        @param y_pos:
        @param create_relaxed_pattern: specifies if pattern shall be printed without optional attributes
        that are not required to create unique match
        @return:
        """

        attr_dict = {}
        # escape lists into strings
        for key, val in self.attrs.items():
            if type(val) in [list, tuple, dict]:
                attr_dict[key] = str(val)
            else:
                attr_dict[key] = val

        # drop p21_id
        attr_dict.pop("p21_id", None)

        if ignore_null_values:
            new_dict = {k: v for k, v in attr_dict.items() if v != "None"}
            attr_dict = new_dict

        if create_relaxed_pattern:
            new_dict = {k: v for k, v in attr_dict.items() if k in ["EntityType", "GlobalId"]}
            attr_dict = new_dict

        node_border_colors = {"PrimaryNode": "#0062b1",
                              "SecondaryNode": "#fcc400",
                              "ConnectionNode": "#68bc00"}

        # build arrows expression
        arrows_node = {
            "id": str(self.get_node_identifier()),
            "position": {
                "x": x_pos,
                "y": y_pos
            },
            "caption": str(self.attrs["p21_id"]),
            "style": {
                "border-color": node_border_colors[self.get_node_type()],
                "radius": 25,
                "property-alignment": "center"
                # "outside-position": "top"
            },
            "properties": attr_dict,

        }
        return arrows_node
