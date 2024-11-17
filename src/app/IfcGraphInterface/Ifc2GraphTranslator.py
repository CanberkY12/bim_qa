""" package import """
from pprint import pprint

import jsonpickle

from neo4j_middleware.Neo4jGraphFactory import Neo4jGraphFactory
from neo4j_middleware.Neo4jQueryFactory import Neo4jQueryFactory
import ifcopenshell
import progressbar

""" file import """


class IFCGraphGenerator:
    """
    IfcP21 to neo4j mapper. 
    Translates a given IFC model in P21 encoding into a propertyGraph 
    """

    # constructor
    """ 
    Public constructor for IFCP21_neo4jMapper
    trigger console output while parsing using the ToConsole boolean
    """

    def __init__(self, connector, model_path, write_to_file=False):
        """

        @param connector: can be null if write_to_file is set to True
        @param model_path:
        @param write_to_file: if False, all commands are directly executed on the connected neo4j db.
                                if set to True, cypher is written to console or *.cypher file
        """

        # try to open the ifc model and load the content into the model variable
        try:
            self.model_path = model_path
            self.model = ifcopenshell.open(model_path)
            ifc_version = self.model.schema
            self.schema = ifcopenshell.ifcopenshell_wrapper.schema_by_name(
                ifc_version)
        except:
            print('file path: {}'.format(model_path))
            raise Exception('Unable to open IFC model on given file path')

        # define the label (i.e., the model timestamp)
        my_label = 'ts' + self.model.wrapped_data.header.file_name.time_stamp
        my_label = my_label.replace('-', '')
        my_label = my_label.replace(':', '')
        self.timestamp = my_label
        self.cypher_statements = []

        # set the connector
        self.connector = connector

        self.write_to_file = write_to_file

        super().__init__()

    def generateGraph(self, validate_result=False):
        """
        parses the IFC model into the graph database
        @return: the label, by which you can identify the model in the database
        """

        if not self.write_to_file:
            # check if model has been already processed
            n = self.connector.run_cypher_statement('MATCH(n:{}) RETURN COUNT(n)'.format(self.timestamp))[0][0]

            if int(n) > 0:
                print('WARNING: entire graph labeled with >> {} << gets overwritten by staged file {}.'.format(
                    self.timestamp, self.model_path))

                self.connector.run_cypher_statement('MATCH(n:{}) DETACH DELETE n'.format(self.timestamp))

        print('[IFC_P21 > {} < ]: Generating graph... '.format(self.timestamp))

        # extract model data

        entity_list = []

        for element in self.model:
            entity_list.append(element)

        increment = 100 / (len(entity_list) * 2)
        percent = 0

        for entity in entity_list:

            # print progressbar
            percent += increment
            progressbar.print_bar(percent)

            # check if the primary_node_type is either an ObjectDef or Relationship or neither
            if entity.is_a('IfcObjectDefinition'):
                self.__map_entity(entity, "PrimaryNode")
            elif entity.is_a('IfcRelationship'):
                self.__map_entity(entity, "ConnectionNode")
            else:
                self.__map_entity(entity, "SecondaryNode")

        for entity in entity_list:
            # print progressbar
            percent += increment
            progressbar.print_bar(percent)

            self.build_node_rels(entity)

        print('[IFC_P21 > {} < ]: Generating graph - DONE. \n '.format(self.timestamp))

        if validate_result:
            self.validate_parsing_result()

        return self.cypher_statements

    def generate_arrows_visualization(self, ignore_null_values: bool = False):
        """
        creates a json that can be used for arrows.app visualization
        """

        # load base
        with open("neo4j_middleware/base_arrows_format.json") as f:
            content = f.read()
        arrows = jsonpickle.decode(content)

        x_pos = 0
        y_pos = 0

        rel_counter = 0
        for entity in self.model:

            # get node data
            attr_dict, entity_type = self.extract_node_data(entity=entity)

            # escape lists into strings
            for key, val in attr_dict.items():
                if type(val) in [list, tuple, dict]:
                    attr_dict[key] = str(val)

            if ignore_null_values:
                new_dict = {k: v for k, v in attr_dict.items() if v is not None}
                attr_dict = new_dict

            # check if the primary_node_type is either an ObjectDef or Relationship or neither
            if entity.is_a('IfcObjectDefinition'):
                node_type = "PrimaryNode"
            elif entity.is_a('IfcRelationship'):
                node_type = "ConnectionNode"
            else:
                node_type = "SecondaryNode"
                # skip secondary nodes
                continue

            node_identifier = attr_dict['p21_id']
            attr_dict.pop("p21_id")

            node_border_colors = {"PrimaryNode": "#0062b1",
                                  "SecondaryNode": "#fcc400",
                                  "ConnectionNode": "#68bc00"}

            # build arrows expression
            arrows_node = {
                "id": "n" + str(node_identifier),
                "position": {
                    "x": x_pos,
                    "y": y_pos
                },
                "caption": str(node_identifier),
                "style": {
                    "border-color": node_border_colors[node_type],
                    "radius": 20
                    # "outside-position": "top"
                },
                "properties": attr_dict,

            }
            arrows["nodes"].append(arrows_node)

            x_pos += 100

            _, single_associations, aggregated_associations = self.separate_attributes(entity)

            for assoc in single_associations:
                # association may be set to None, then continue

                target = entity.get_info()[assoc]
                if target is None:
                    continue

                # build arrows expression
                rel = {
                    "id": "n" + str(rel_counter),
                    "type": "REL",
                    "style": {},
                    "type": assoc,
                    "fromId": "n" + str(node_identifier),
                    "toId": "n" + str(target.get_info()["id"])
                }

                arrows["relationships"].append(rel)

                rel_counter += 1

            list_item = 0
            for agg_assoc in aggregated_associations:

                targets = entity.get_info()[agg_assoc]
                if targets is None:
                    print("Havent found target: TargetName: {}".format(agg_assoc))
                    continue

                for target in targets:
                    if target is None:
                        continue

                    # build arrows expression
                    rel = {
                        "id": "n" + str(rel_counter),
                        "type": "REL",
                        "style": {},
                        "type": agg_assoc,
                        "properties": {
                            "listItem": str(list_item)
                        },
                        "fromId": "n" + str(node_identifier),
                        "toId": "n" + str(target.get_info()["id"])
                    }

                    arrows["relationships"].append(rel)
                    list_item += 1

                rel_counter += 1

        # save
        model_path = self.model_path
        save_path = model_path[:-4] + "_arrowsVis.json"
        f = open(save_path, 'w')
        f.write(jsonpickle.dumps(arrows, unpicklable=True))
        f.close()

    def validate_parsing_result(self):
        """
        Compares the number of entities in the model with the number of nodes in the graph
        @return: boolean
        """

        # get number of nodes in the graph
        cy = Neo4jQueryFactory.count_nodes(self.timestamp)
        count_graph = self.connector.run_cypher_statement(cy, 'count')[0]

        # get number of entities in the model
        count_model = len(list(self.model))

        # compare and calculate diff
        if count_graph == count_model:
            print(
                'Validation successful. Number of entities in the file equal the number of nodes in the graph.')
            return True
        else:
            print('Validation unsuccessful. '
                  'Number of entities in the file do not equal the number of nodes in the graph.'
                  '\nDifference: {}'.format(abs(count_graph - count_model)))
            return False

    def __map_entity(self, entity, label) -> str:
        """
        translates an IFC instance into a neo4j node
        """

        node_properties_dict, entity_type = self.extract_node_data(entity)

        # run cypher command
        cypher_statement = Neo4jGraphFactory.merge_node_with_attr(label=label,
                                                                  attrs=node_properties_dict,
                                                                  timestamp=self.timestamp,
                                                                  entity_type=entity_type,
                                                                  node_identifier=node_properties_dict['p21_id'],
                                                                  skip_return=True)
        if self.write_to_file:
            print(cypher_statement)
        else:
            self.connector.run_cypher_statement(cypher_statement)
        self.cypher_statements.append(cypher_statement)

        return cypher_statement

    def build_node_rels(self, entity):
        # get info
        info = entity.get_info()
        p21_id = info['id']

        # get attribute definitions
        _, single_associations, aggregated_associations = self.separate_attributes(entity)

        for association_name in single_associations:

            # get associated entity
            associated_entity = info[association_name]

            if associated_entity is None:
                continue

            # traverse to the associated entity and query p21 id
            p21_id_child = associated_entity.get_info()['id']

            if not isinstance(p21_id_child, int):
                raise Exception("help")

            edge_attrs = {'rel_type': association_name}

            # merge with existing
            if self.write_to_file:
                cy = Neo4jGraphFactory.merge_on_p21(
                    p21_id, p21_id_child, edge_attrs, self.timestamp, without_match=True)
                print(cy)
            else:
                cy = Neo4jGraphFactory.merge_on_p21(
                    p21_id, p21_id_child, edge_attrs, self.timestamp, without_match=False)
                self.connector.run_cypher_statement(cy)
            self.cypher_statements.append(cy)

        for association_name in aggregated_associations:
            entities = info[association_name]

            if entities is None:
                # detected an array of associations but nothing was referenced within the given instance model
                continue
            self.build_aggregated_associations(association_name=association_name, parent_p21=p21_id,
                                               child_entities=entities)

    def build_aggregated_associations(self, association_name: str, parent_p21: int, child_entities):

        select_problem = False

        i = 0
        for associated_entity in child_entities:

            try:
                p21_id_child = associated_entity.get_info()['id']

                edge_attrs = {
                    'rel_type': association_name,
                    'listItem': i
                }

            except:
                if type(child_entities) is tuple:
                    print("Found issue when building relationships")
                    print("Child entity is: ", child_entities)
                elif type(child_entities) is str:
                    print("Found issues when building relationship")
                    print("Child entity is: ", child_entities)

                if child_entities.is_a() == "IfcPropertySet":
                    select_problem = True
                # in some weird cases, ifcopenshell fails to traverse objectified relationships
                child_guid = child_entities.GlobalId

                cy = 'MATCH (n{{GlobalId: \"{}\"}}) RETURN n.p21_id'.format(child_guid)

                if self.write_to_file:
                    print(cy)
                else:
                    raw = self.connector.run_cypher_statement(cy)[0]
                    p21_id_child = int(raw[0])

                edge_attrs = {
                    'rel_type': association_name
                }

            # merge with existing

            if self.write_to_file:
                cy = Neo4jGraphFactory.merge_on_p21(
                    parent_p21, p21_id_child, edge_attrs, self.timestamp, without_match=True)
                print(cy)
            else:
                cy = Neo4jGraphFactory.merge_on_p21(
                    parent_p21, p21_id_child, edge_attrs, self.timestamp, without_match=False)
                self.connector.run_cypher_statement(cy)
            self.cypher_statements.append(cy)

            # increase counter
            i += 1

            if select_problem:
                break

    def separate_attributes(self, entity) -> tuple:
        """"
        Queries all attributes of the corresponding primary_node_type definition and returns if an attribute has
        attr type value, an primary_node_type value or is an aggregation of entities
        @primary_node_type:
        @return:
        """
        info = entity.get_info()
        clsName = info['type']
        entity_id = info['id']

        # remove entity_id and type
        # info.pop('id')
        # info.pop('type')

        # get the class definition for the current instance w.r.t. schema version
        # https://wiki.osarch.org/index.php?title=IfcOpenShell_code_examples#Exploring_IFC_schema

        # separate attributes into node attributes, simple associations, and sets of associations
        node_attributes = []
        single_associations = []
        aggregated_associations = []

        try:
            class_definition = self.schema.declaration_by_name(
                clsName).all_attributes()
        except:
            raise Exception("Failed to query schema specification in IFC2GraphTranslator.\n "
                            "Schema: {}, Entity: {} ".format(self.schema, clsName))

        for attr in class_definition:
            # check if attribute has attr value in the current primary_node_type instance
            # if info[name] is not None:
            #     print('attribute present')
            # else:
            #     print('attribute empty')
            #     continue

            # this is attr quite weird approach but it works
            try:
                attr_type = attr.type_of_attribute().declared_type()
            except:
                attr_type = attr.type_of_attribute()

            # get the value structure
            is_entity = isinstance(
                attr_type, ifcopenshell.ifcopenshell_wrapper.entity)
            is_type = isinstance(
                attr_type, ifcopenshell.ifcopenshell_wrapper.type_declaration)
            is_select = isinstance(
                attr_type, ifcopenshell.ifcopenshell_wrapper.select_type)

            is_pdt_select = False
            is_entity_select = False
            is_nested_select = False
            is_enumeration = isinstance(
                attr_type, ifcopenshell.ifcopenshell_wrapper.enumeration_type)
            is_aggregation = isinstance(
                attr_type, ifcopenshell.ifcopenshell_wrapper.aggregation_type)

            # ToDo: Distinguish if it is a select of entities or a select of predefinedTypes
            if is_select:
                # methods = attr.type_of_attribute().declared_type()
                # print(dir(methods))
                lst = attr.type_of_attribute().declared_type().select_list()

                is_entity_select = all(
                    [isinstance(x, ifcopenshell.ifcopenshell_wrapper.entity) for x in lst])
                is_pdt_select = all(
                    [isinstance(x, ifcopenshell.ifcopenshell_wrapper.type_declaration) for x in lst])
                is_nested_select = all(
                    [isinstance(x, ifcopenshell.ifcopenshell_wrapper.select_type) for x in lst])

                # handle mixed cases
                if isinstance(lst[0], ifcopenshell.ifcopenshell_wrapper.entity) \
                        and isinstance(lst[1], ifcopenshell.ifcopenshell_wrapper.type_declaration):
                    is_aggregation = True

            # catch some weird cases with IfcDimensionalExponents
            #  as this primary_node_type doesnt use types but atomic attr declarations
            if attr.name() in ['LengthExponent',
                               'MassExponent',
                               'TimeExponent',
                               'ElectricCurrentExponent',
                               'ThermodynamicTemperatureExponent',
                               'AmountOfSubstanceExponent',
                               'LuminousIntensityExponent',
                               'Exponent',  # from IfcDerivedUnitElement
                               'Precision',  # from IfcGeometricRepresentationContext
                               'Scale',  # from IfcCartesianPointTransformationOperator3D in 2x3
                               'Orientation',  # from IfcFaceOuterBound in 2x3
                               'SelfIntersect',  # from IfcCompositeCurve in 2x3
                               'SameSense',  # from IfcCompositeCurveSegment in IFC2x3
                               'SenseAgreement',  # from IfcTrimmedCurve in IFC2x3
                               'AgreementFlag',  # from IfcPolygonalBoundedHalfSpace
                               'ParameterTakesPrecedence',
                               'ClosedCurve',
                               'SelfIntersect',
                               'LayerOn',
                               'LayerFrozen',
                               'LayerBlocked',
                               'ProductDefinitional',
                               'Scale2',  # IfcCartesianTransformationOperator2DnonUniform
                               'Scale3',
                               'RelatedPriorities',
                               'RelatingPriorities',
                               'SameSense',
                               'AgreementFlag',
                               'USense',
                               'VSense',
                               'WeightsData',
                               'Weights',
                               'Sizeable',
                               'ParameterTakesPrecedence',
                               'IsCritical',
                               'DestabilizingLoad',
                               'IsLinear',
                               'RepeatS',
                               'RepeatT',
                               'IsHeading',
                               'IsMilestone',
                               'Priority',
                               'SenseAgreement',
                               'IsPotable',
                               'NumberOfRiser',
                               'NumberOfTreads',
                               'Pixel',
                               'InputPhase',
                               'Degree',
                               'CurveFont',
                               'DiffuseColour',
                               'TransmissionColour',
                               'DiffuseTransmissionColour',
                               'ReflectionColour',
                               'SpecularColour',
                               'ColourList',
                               'ColourIndex',
                               'NominalValue',
                               'AddressLines',
                               'StartOfNextHatchLine'

                               ]:
                node_attributes.append(attr.name())

            elif is_type or is_enumeration or is_pdt_select or is_nested_select:
                node_attributes.append(attr.name())
            elif is_entity or is_entity_select:
                single_associations.append(attr.name())
            elif is_aggregation:
                # ToDo: check if it is an aggregation of types or an aggregation of entities
                # https://standards.buildingsmart.org/IFC/RELEASE/IFC4/ADD2_TC1/HTML/link/ifctrimmedcurve.htm -> trimSelect
                if attr.name() in [
                    'Coordinates',
                    'DirectionRatios',
                    'CoordList',
                    'segments',
                    'MiddleNames',
                    'PrefixTitles',
                    'SuffixTitles',
                    'Roles',
                    'Addresses',
                    'CoordIndex',
                    'InnerCoordIndices',
                    'Trim1',
                    'Trim2',
                    'Orientation',
                    'RefLongitude',
                    'RefLatitude',
                    'NominalValue'
                ]:
                    node_attributes.append(attr.name())
                else:
                    aggregated_associations.append(attr.name())
            else:
                raise Exception('Tried to encode the attribute type of primary_node_type #{} clsName: {} attribute {}. '
                                'Please check your graph translator.'.format(entity_id, clsName, attr.name()))
        node_attributes.append('id')
        node_attributes.append('type')
        return node_attributes, single_associations, aggregated_associations

    def extract_node_data(self, entity):
        """
        extracts the relevant information from a given IFC entity instance. Returns the label,
        @param entity:
        @return:
        """

        # get some basic data
        info = entity.get_info()

        # node_properties, single_associations, aggregated_associations = self.separate_attributes(primary_node_type)
        node_properties, _, _ = self.separate_attributes(entity)

        # create a dictionary of properties
        node_properties_dict = {}
        for p_name in node_properties:
            p_val = info[p_name]

            if p_name == 'NominalValue':
                wrapped_val = p_val.wrappedValue
                p_val = 'IfcLabel({})'.format(str(wrapped_val).replace("'", ""))
                p_val = str(p_val)
                # ToDo: consider this workaround when translating a graph back in its SPF representation

            node_properties_dict[p_name] = p_val

        # rename some keys
        node_properties_dict['p21_id'] = node_properties_dict.pop('id')
        node_properties_dict['EntityType'] = node_properties_dict.pop('type')

        entity_type = node_properties_dict['EntityType']

        return node_properties_dict, entity_type
