import { ApolloServer, gql } from 'apollo-server';
import ifc2json from 'ifc2json';

export default async function sendQuery(userInput) {


    // Sample IFC file path
    const ifcFilePath = 'path/to/your.ifc';

    // Convert IFC to JSON
    const ifcData = ifc2json.convert(ifcFilePath);

    // Define GraphQL schema
    const typeDefs = gql`
    type Element {
        id: ID!
        name: String
        type: String
        properties: [Property]
    }

        type Property {
        name: String
        value: String
    }

        type Query {
        elements(type: String, name: String): [Element]
        element(id: ID!): Element
    }
    `;

    // Define resolvers
    const resolvers = {
    Query: {
        windows: () => {
        // Extract windows from IFC data
        return ifcData.elements.filter(element => element.type === 'IfcWindow');
        },
        window: (parent, args) => {
        // Find a specific window by ID
        return ifcData.elements.find(element => element.id === args.id && element.type === 'IfcWindow');
        },
    },
    };

    // Create Apollo Server
    const server = new ApolloServer({ typeDefs, resolvers });

    // Start the server
    server.listen().then(({ url }) => {
    console.log(`🚀 Server ready at ${url}`);
    });
}