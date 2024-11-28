import logging
import re
import os
import dotenv

from neo4j import GraphDatabase
from neo4jGraphDiff.Config.Configuration import Configuration

# example of how to configure the logger
# the logger needs to be built within the module it is supposed to be used in, but the it can be configured elsewhere.
config = Configuration.basic_config()
logsetting = config.LogSettings
logger = logging.getLogger(__name__)
logger = logsetting.initialize_logger(logger)


class Neo4jConnector:
    """ handles the connection to a given neo4j database """
    # member variables
    
    my_driver = []

    # constructor
    def __init__(self):
        pass

    # methods
    def connect_driver(self):
        """
        creates a new connection to the database
        @return:
        """
        url=dotenv.get_key(".env" ,"url")
        username=dotenv.get_key(".env" ,"username")
        password=dotenv.get_key(".env" ,"password")
        #username=os.getenv("username")
        #password=os.getenv("password")
        #url=os.getenv("url")
        try:
            self.my_driver = GraphDatabase.driver(url, auth=(username, password))
        except self.my_driver:
            logger.error('Connection failed')
            raise Exception("Oops!  Connection failed.  Try again...")

    def run_cypher_statement(self, statement, postStatement = None):
        """
        executes a given cypher statement and does some post processing if stated
        @statement: cypher command
        @postStatement: post processing of response
        @return
        """

        if self.checkForSpecialCharacters(statement) == False:
            logger.warning(
                "Potential errors in cypher command (single quotes within single quotes?)\n" +
                "The following cypher command could fail when executing:\n{}".format(statement))

        try:
            with self.my_driver.session() as session:
                with session.begin_transaction() as tx:
                    logger.info("[neo4j_connector] Running query: " + str(statement)[:80] + '...')

                    res = tx.run(statement)
                    logger.info("[neo4j_connector] Query delta: " + str(res))
                    return_val = []

                    if postStatement != None:
                        for record in res:
                            # print(record[postStatement])
                            return_val.append(record[postStatement])

                    else:
                        for record in res:
                            # print(record)
                            return_val.append(record)
                logger.info('[neo4j_connector] Received response. ')
                return return_val

        except:

            logger.error('[neo4j_connector] something went wrong. Check the neo4j connector. ')
            logger.error('[neo4j_connector] Tried to execute cypher statement >> {} <<'.format(statement))
            logger.error('[neo4j_connector] Possible issues: ' +
                         '\t Incorrect cypher statement' +
                         '\t Missing packages inside the graph database \n')
            raise Exception('Error in neo4j Connector.')

    def disconnect_driver(self):
        """
        disconnects the connector instance
        @return:
        """
        self.my_driver.close()
        logger.info('Driver disconnected.')

    def checkForSpecialCharacters(self, statement: str) -> bool:
        """
        Checks for special characters which can cause problems for the cypher interpreter
        @param statement: The cypher statement in question
        @return: 'True' if all is good, 'False' if there could be problems, e.g. single quotes within single quotes
        """
        # Get all substrings within curly brackets
        res_list = re.findall(r'\{}.*?\}', statement)

        # iterate over all substrings
        for res in res_list:
            # split the substring by commas
            res = res.split(',')

            # iterate over those substrings
            for item in res:
                # if there are more than 2 single quotes in a substring, there will be a cypher error
                if item.count("'") > 2:
                    return False
        
        # otherwise, return true
        return True
