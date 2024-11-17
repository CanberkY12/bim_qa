from typing import List

from neo4j_middleware.ResponseParser.NodeItem import NodeItem


class NodeMatchingTable:

    def __init__(self):
        self.matched_nodes: List[NodePair] = []

    def add_matched_nodes(self, node1: NodeItem, node2: NodeItem):
        """
        appends a single NodePair instance to the list and checks existence upfront
        @param node1:
        @param node2:
        @return:
        """
        pair = NodePair(node1, node2)
        if pair not in self.matched_nodes:
            self.matched_nodes.append(pair)

    def append_pairs(self, matchedNodes):
        """
        appends a list of NodePair items and checks if they already exist in the parent list
        @param matchedNodes:
        @return:
        """
        for pair in matchedNodes.matched_nodes:
            if pair not in self.matched_nodes:
                self.matched_nodes.append(pair)

    def get_all_init_nodes(self):
        return [x.init_node for x in self.matched_nodes]

    def get_all_updated_nodes(self):
        return [x.updated_node for x in self.matched_nodes]

    def node_involved_in_nodePair(self, node: NodeItem):
        """
        returns true if nodeItem is captured within a node pair
        @param node:
        @return:
        """
        if node in self.get_all_init_nodes():
            return True
        elif node in self.get_all_updated_nodes():
            return True
        else:
            return False

    def node_pair_in_matching_table(self, pair):
        """
        returns true if a NodePair item is already listed in the matching table
        @param pair:
        @return:
        """
        if pair in self.matched_nodes:
            return True
        else:
            return False

    def get_all_primaryNode_pairs(self):
        return [p for p in self.matched_nodes if
                (p.init_node.get_node_type() == "PrimaryNode" and p.updated_node.get_node_type() == "PrimaryNode")]

    def __repr__(self):
        return 'NodeMatchingTable NumEntries: {}'.format(len(self.matched_nodes))

    def get_parent_primaryNode(self, subgraphNode: NodeItem):
        """
        returns the primaryNode from which a secondary node was detected the first time
        @param subgraphNode:
        @return:
        """

        # get position of node
        lst_position: int
        node_list = []

        if subgraphNode in self.get_all_init_nodes():
            lst_position = self.get_all_init_nodes().index(subgraphNode)
            node_list = self.get_all_init_nodes()[:lst_position]

        elif subgraphNode in self.get_all_updated_nodes():
            lst_position = self.get_all_updated_nodes().index(subgraphNode)
            node_list = self.get_all_updated_nodes()[:lst_position]

        try:
            # find next primaryNode in the list by reversing and find first index
            parent_primary_node = [prim_node for prim_node in node_list[::-1]
                                   if prim_node.get_node_type() == "PrimaryNode"][0]
        except:
            # some situations are not yet implemented
            return None

        # return node_list[::-1].index(parent_primary_node)
        return parent_primary_node



class NodePair:
    def __init__(self, init: NodeItem, updated: NodeItem):
        self.init_node: NodeItem = init
        self.updated_node: NodeItem = updated

    def __repr__(self):
        return 'NodePair: entity_type: {} ID_init: {} ID_updated: {}'.format(
            self.init_node.get_entity_type(),
            self.init_node.id,
            self.updated_node.id)

    def __eq__(self, other):
        if self.init_node.id == other.init_node.id and self.updated_node.id == other.updated_node.id:
            return True
        else:
            return False

