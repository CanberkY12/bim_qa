""" package import """
import logging
import time
from datetime import datetime

""" class import """
from IfcGraphInterface.Ifc2GraphTranslator import IFCGraphGenerator
from neo4j_middleware.neo4jConnector import Neo4jConnector

# --- Script ---

# init logging
current_date_and_time = datetime.now().strftime("%Y-%m-%d-%H-%M-%S")
logging.basicConfig(filename='{}.neo4j-query-log.log'.format(current_date_and_time), level=logging.INFO)
logging.info('Started')


def main():
    print('Parsing Ifc StepP21 model to Neo4j.... \n')
    print('connecting to neo4j database... ')
    connector = Neo4jConnector()
    connector.connect_driver()

    # # These lines all filepaths in the directory 'dir'
    # dir = './00_sampleData/IFC_stepP21/**/*.ifc'
    # paths = []
    # for filepath in glob.glob(dir, recursive=True):
    #    paths.append(filepath)
    # print(paths)

    # paths = [
    #     '00_sampleData/IFC_stepP21/diss-casestudy/TW-v1.ifc',
    #     '00_sampleData/IFC_stepP21/diss-casestudy/TW-v2.ifc'
    # ]
    paths = [
        '00_sampleData/IFC_stepP21/diss-casestudy/ARC-v1-purified.ifc',
        '00_sampleData/IFC_stepP21/diss-casestudy/ARC-v2-purified.ifc',
        '00_sampleData/IFC_stepP21/diss-casestudy/ARC-v3-purified.ifc'
    ]

    for p in paths:
        print(p)

    print('Starting to generate graphs...')
    amount = len(paths)
    start = time.perf_counter()
    for idx, path in enumerate(paths):
        # parse model
        graph_generator = IFCGraphGenerator(connector, path, write_to_file=False)
        print('Generating Graph %d/%d' % (idx + 1, amount))
        graph_generator.generateGraph()
    finish = time.perf_counter()
    print('100% done. Graphs generated. Finished in {} seconds.'.format(round(finish - start, 2)))

    print("Performing post-processing: Remove layer assignments and styled items ")

    cy = 'MATCH p = (n{EntityType:"IfcStyledItem"})-[r:rel]->(s:SecondaryNode) DELETE r'
    connector.run_cypher_statement(cy)

    cy = 'MATCH p = (n{EntityType:"IfcPresentationLayerAssignment"})-[r:rel]->(s:SecondaryNode) DELETE r'
    connector.run_cypher_statement(cy)

    print("Post-processing done. ")

    # disconnect from database
    connector.disconnect_driver()


if __name__ == '__main__':
    main()
