import { session } from 'neo4j-driver';
import neo4j from 'neo4j-driver';
import dotenv from 'dotenv';
import spawn from "child_process";

(async () => {
    
    dotenv.config({
      path: "C:/Users/berky/Downloads/Neo4j-be20d4fc-Created-2024-10-22.txt",
      debug: true  // to raise file/parsing errors
    })
  
    const URI = process.env.NEO4J_URI
    const USER = process.env.NEO4J_USERNAME
    const PASSWORD = process.env.NEO4J_PASSWORD
    let driver
  
    try {
      driver = neo4j.driver(URI,  neo4j.auth.basic(USER, PASSWORD))
      const serverInfo = await driver.getServerInfo()
      console.log('Connection established')
      console.log("serverinfo: ", serverInfo)
    } catch(err) {
      console.log(`Connection error\n${err}\nCause: ${err.cause}`)
      await driver.close()
      return
    }
    spawn.exec("C:/Users/berky/Downloads/Neo4j-be20d4fc-Created-2024-10-22.txt")

    // Use the driver to run queries
    await driver.close()
  })();