from typing import List

from neo4jGraphDiff.Caption.NodeMatchingTable import NodePair
from .Neo4jFactory import Neo4jFactory


class Neo4jQueryFactory(Neo4jFactory):
    """ provides a set of methods to create cypher strings querying the neo4j database"""
    def __init__(self):
        pass

    @classmethod
    def diff_nodes(cls, node_id_left: int, node_id_right: int) -> str:
        """Calculates the attribute diff between two nodes and returns a cypher string.
        !! APOC library needs to be installed in the database instance !!

        Parameters
        ----------
        node_id_left : left node to be compared
        node_id_right: right node to be compared

        Returns
        -------
        cypher string to be executed using a connector instance.

        """
        query_left = 'MATCH (l) WHERE ID(l) = {}'.format(node_id_left)
        query_right = 'MATCH (r) WHERE ID(r) = {}'.format(node_id_right)
        ret_statement = 'RETURN apoc.diff.nodes(l,r)'
        return Neo4jFactory.BuildMultiStatement([query_left, query_right, ret_statement])

    @classmethod
    def get_nodeId_byP21(cls, p21_id: int, label: str = None):
        """ returns a cypher statement to query a node by its P21_id and a given (optional) label. """

        if label is not None:
            query = 'MATCH (n:{})'.format(label)
        else:
            query = 'MATCH (n)'

        wh = 'WHERE n.p21_id = {}'.format(p21_id)
        ret_statement = 'RETURN ID(n)'
        return Neo4jFactory.BuildMultiStatement([query, wh, ret_statement])

    @classmethod
    def get_primary_nodes(cls, label: str) -> str:
        """
        Queries all primary nodes, which have the given label attached.
        @param label:
        @return: cypher query string
        """
        match = 'MATCH p = (n:PrimaryNode:{}) '.format(label)
        ret_statement = 'RETURN n'
        return Neo4jFactory.BuildMultiStatement([match, ret_statement])

    @classmethod
    def get_connection_nodes(cls, label: str) -> str: 
        """
        Queries all primary nodes, which have the given label attached.
        @param label:
        @return: cypher query string
        """
        match = 'MATCH (n:ConnectionNode:{}) '.format(label)
        ret_statement = 'RETURN n'
        return Neo4jFactory.BuildMultiStatement([match, ret_statement])

    @classmethod
    def get_all_nodes(cls, label:str) -> str:
        """
        queries all nodes with a specific label
        @param label:
        @return: cypher query string
        """
        cy = "MATCH (n:{}) RETURN n".format(label)
        return cy

    @classmethod
    def get_all_edge_patterns(cls, label: str) -> str:
        cy = "MATCH pattern = (n:{0})-[r:rel]->(m:{0}) " \
             "RETURN pattern, NODES(pattern), RELATIONSHIPS(pattern)".format(label)
        return cy

    @classmethod
    def get_hash_by_nodeId(cls, label: str, nodeId: int, attrIgnoreList=None) -> str:
        """
        Calculates the hash_value sum over a given node.
        Use attrIgnoreList to specify attribute names that should be excluded when calculating the hash_value
        @param label: model label
        @param nodeId: the node ID
        @param attrIgnoreList: attributes to be ignored in the hash_value calculation
        @return: cypher query string
        """

        getModel = 'MATCH(n)'.format(label)
        where = 'WHERE ID(n) = {}'.format(nodeId)

        open_sub = 'CALL {WITH n'

        removeLabel = 'REMOVE n:{}'.format(label)

        # apply diffIgnore attributes if staged
        if attrIgnoreList == None:
            calc_fingerprint = "with apoc.hashing.fingerprint(n) as hash RETURN hash"
        else:
            # define function where quotationmarks "" or [] are added
            def surroundStrings(l):
                return ['"' + x + '"' for x in l]
            
            ignore_str = surroundStrings(attrIgnoreList)
            # define separator
            separator = ', '

            # join the contents of the list with the separator
            ignore_str = separator.join(ignore_str)

            # close the string with []
            ignore_str = '[' + ignore_str + ']'
 
            calc_fingerprint = 'with apoc.hashing.fingerprint(n, {}) as hash RETURN hash'.format(ignore_str)

        close_sub = '}'
        add_label_again = 'SET n:{}'.format(label)
        return_results = 'RETURN hash'
        return Neo4jFactory.BuildMultiStatement([getModel, where, open_sub, removeLabel, calc_fingerprint, close_sub, add_label_again, return_results])


    @classmethod
    def get_child_nodes(cls, label: str, parent_node_id: int) -> str:
        """
        search for all nodes that have an incoming edge from the specified parent node and carries the similar label
        @param label: model identifier
        @param parent_node_id: the node id of the parent node
        @return: cypher query string
        """
        match = 'MATCH (n:{})-[r:rel]->(c)'.format(label)
        where = 'WHERE ID(n) = {}'.format(parent_node_id)
        ret = 'RETURN c, PROPERTIES(r)'
        return Neo4jFactory.BuildMultiStatement([match, where, ret])

    
    @classmethod
    def get_node_by_id(cls, nodeId: int) -> str:
        return 'MATCH (n) WHERE ID(n)={} RETURN n'.format(nodeId)

    @classmethod
    def get_hierarchical_prim_nodes(cls, node_id: int, exclude_nodes: List[NodePair] = []) -> str:
        va = ''
        for n in exclude_nodes:
            va += '{}, {}, '.format(n.init_node.id, n.updated_node.id)

        return """
            MATCH (n)<-[r1]-(c:ConnectionNode)-[r2]->(m:PrimaryNode) 
            WHERE ID(n) = {} AND NOT r1 = r2 AND NOT(ID(m) IN [{}])
            RETURN DISTINCT m
            """.format(node_id, va[:-2])

    @classmethod
    def nodes_are_connected(cls, node_id_a: int, node_id_b: int) -> str:
        """
        checks if two given nodes have a directed edge from a to b
        @param node_id_a: node a 
        @param node_id_b: node b
        @return: cypher query string
        """
        match_a = 'MATCH (n) WHERE ID(n) = {}'.format(node_id_a)
        match_b = 'MATCH (m) WHERE ID(m) = {}'.format(node_id_b)
        ret = 'RETURN exists((n)-[]->(m)) as are_connected'
        return Neo4jFactory.BuildMultiStatement([match_a, match_b, ret])

    @classmethod
    def get_directed_path_by_nodeId(cls, node_id_start: int, node_id_target: int) -> str:
        """
        queries the path between two nodes
        @param node_id_start: node id of start node
        @param node_id_target: node id of target node
        @return: cypher query string
        """
        match_start = 'MATCH(n) WHERE ID(n) = {}'.format(node_id_start)
        match_target = 'MATCH(m) WHERE ID(m) = {}'.format(node_id_target)
        path = 'MATCH p = shortestPath((n)-[*..15]->(m))' # max path length is hardcoded to 15
        ret = 'RETURN p as path, NODES(p), RELATIONSHIPS(p)'
        return Neo4jFactory.BuildMultiStatement([match_start, match_target, path, ret])

    @classmethod
    def get_pattern_by_node_id(cls, node_id: int) -> str:
        """

        @param node_id:
        @return: cypher query string
        """
        match = 'MATCH pattern = (n)-[*..10]->(m)'
        where = 'WHERE ID(n) = {}'.format(node_id)
        ret = 'RETURN pattern, NODES(pattern), RELATIONSHIPS(pattern)'
        return Neo4jFactory.BuildMultiStatement([match, where, ret])

    @classmethod
    def get_outgoing_rel_types(cls, node_id: int):
        """
        Queries
        @param node_id:
        @return: cypher query string
        """
        match1 = 'match p = (n) Where ID(n)={}'.format(node_id)
        match2 = 'match (n)-[r]->(f)'
        ret = 'UNWIND r.rel_type as mylist RETURN mylist'
        return Neo4jFactory.BuildMultiStatement([match1, match2, ret])

    @classmethod
    def get_distinct_paths_from_node(cls, node_id: int) -> str:
        """
        Queries all distinct paths outgoing from a specified node
        @param node_id:
        @return: cypher query string
        """
        match1 = 'MATCH p = (n) WHERE ID(n)={}'.format(node_id)
        match2 = 'MATCH paths = (n)-[*..12]->(leaf)' # max length is set to 12!
        cond = 'WHERE NOT (leaf)-->()' # no outgoing edges
        ret = 'RETURN paths, NODES(paths), RELATIONSHIPS(paths)'
        return Neo4jFactory.BuildMultiStatement([match1, match2, cond, ret])

    @classmethod
    def get_primary_structure(cls, label: str) -> str:
        """
        Queries all nodes and edges involved in the primary structure
        @param label: model label
        @return: cypher query string
        """
        pattern = 'MATCH pattern = (n:{}}:PrimaryNode)<--(con)'.format(label)
        ret = 'RETURN pattern'
        return Neo4jFactory.BuildMultiStatement([pattern, ret])

    @classmethod
    def get_conNodes_patterns(cls, node_id: int) -> str:
        return 'MATCH paths = (c:ConnectionNode)-[r]->(n) WHERE ID(c) = {} ' \
               'RETURN paths, NODES(paths), RELATIONSHIPS(paths)'.format(node_id)

    @classmethod
    def get_node_exists(cls, p21_id: int, label: str) -> str:
        """

        @param p21_id:
        @param label:
        @return: cypher query string
        """
        cy = 'OPTIONAL Match(n:{} {{p21_id: {} }}) RETURN n IS NOT NULL AS existing'.format(label, p21_id)
        return cy

    @classmethod
    def get_relationship_attributes(cls, rel_id: int) -> str:
        """
        queries all properties attached to a graph edge
        @param rel_id: the relationship ID
        @return:
        """
        cy = 'MATCH (n)-[r]->(m) WHERE ID(r) = {} RETURN PROPERTIES(r)'.format(rel_id)
        return cy

    @classmethod
    def get_parent_connection_node(cls, node_id: int):
        return 'MATCH path = (c:ConnectionNode)-[r]->(n) WHERE ID(n)={} ' \
               'RETURN path, NODES(path), RELATIONSHIPS(path)'.format(node_id)

    @classmethod
    def get_all_nodes_wou_EQUIVALENTTO_rel(cls, timestamp: str) -> str:
        """
        queries all nodes that do not have an incoming or outgoing SIMILAR_TO relationship
        @param timestamp: the model's identifier
        @return: cypher query string
        """
        cy = """
        Match (n)-[r:EQUIVALENT_TO]-(m) 
        WITH collect(ID(n)) as nodeIds
        MATCH (a:{0}) WHERE NOT ID(a) IN nodeIds
        RETURN a
        """.format(timestamp)
        return cy

    @classmethod
    def get_all_relationships(cls, timestamp: str) -> str:
        """
        queries all relationships of a model and returns raw data to instantiate a GraphPattern instance
        @param timestamp: the model's identifier
        @return: cypher query string
        """
        return """MATCH pa = (n:{0})-[r:rel]->(m:{0}) RETURN pa, NODES(pa), RELATIONSHIPS(pa)""".format(timestamp)


    @classmethod
    def load_SIMILAR_TO_rectangles(cls, ts_init: str, ts_updt: str):
        return """
        MATCH (init_start:{0})-[r1:rel]->(init_end:{0})
        MATCH (updt_start:{1})-[r2:rel]->(updt_end:{1})

        MATCH (init_start)-[s1:SIMILAR_TO]-(updt_start)
        MATCH (init_end)-[s2:SIMILAR_TO]-(updt_end)

        RETURN ID(init_start), ID(init_end), ID(updt_start), ID(updt_end)
        """.format(ts_init, ts_updt)

    @classmethod
    def get_modified_edge_IDs(cls, ts_init: str, ts_updt: str) -> str:
        return """
        MATCH (init_start:{0})-[r1:rel]->(init_end:{0})
        MATCH (updt_start:{1})-[r2:rel]->(updt_end:{1})

        MATCH (init_start)-[s1:SIMILAR_TO]-(updt_start)
        MATCH (init_end)-[s2:SIMILAR_TO]-(updt_end)

        // unwind all edge IDs
        WITH COLLECT(ID(r1)) as edgeIds_init, COLLECT(ID(r2)) as edgeIds_updt

        // find all edges that are not included in this pattern but belong to the specified timestamps
        MATCH (a:{0})-[mod_init:rel]->(b:{0}) WHERE NOT ID(mod_init) IN edgeIds_init
        MATCH (c:{1})-[mod_updt:rel]->(d:{1}) WHERE NOT ID(mod_updt) IN edgeIds_updt

        RETURN ID(mod_init) as modifiedEdgeIDs_init, ID(mod_updt) as modifiedEdgeIDs_updated
        """.format(ts_init, ts_updt)

# ticket_PostEvent-VerifyParsedModel
    @classmethod
    def count_nodes(cls, timestamp):
        """
        Provides the cypher command to return the number of nodes of a graph
        @param timestamp: timestamp of the graph
        @return: cypher command as str
        """
        return 'Match(n:{}) RETURN count(n) AS count'.format(timestamp)
