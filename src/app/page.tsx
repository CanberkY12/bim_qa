"use client"
 
import { useState, useEffect, useRef } from 'react'
import { Input } from "@/components/ui/input"
import MaxWidthWrapper from "./components/MaxWidthWrapper";
import ClickComponent from "./components/ButtonReciever";
import { ArrowRight } from "lucide-react"
import { buttonVariants } from "@/components/ui/button";
import { LoginLink } from "@kinde-oss/kinde-auth-nextjs";
import { Html } from 'next/document';
import { useRouter } from 'next/router';
import * as BUI from "@thatopen/ui";

import PropertiesPanel from 'C:/Users/berky/oxide/src/ui/PropertiesPanel';
import { ElementPropertiesUI } from '../../thatOpenSrc/engine_ui-components/packages/obc/src/components/tables/ElementProperties/src/template';
import * as CUI from "C:/Users/berky/oxide/thatOpenSrc/engine_ui-components/packages/obc/src/components";

import * as WEBIFC from "web-ifc";
import { IfcLoader } from "@thatopen/components";


import * as OBC from "@thatopen/components";
import * as OBCF from "@thatopen/components-front";
import { FragmentsGroup } from "@thatopen/fragments";
import { viewport } from '../../thatOpenSrc/engine_ui-components/packages/obc/src/components/tables/ElementProperties/example';
import sendInput from "C:/Users/berky/oxide/src/app/llmGraphQL/promptreceiver.js"
import sendQuery from "C:/Users/berky/oxide/src/app/server.js"
import NeoVis, { NeovisConfig } from "neovis.js/dist/neovis.js";




export default function Home() {
  const [propertiesTable, setPropertiesTable] = useState<any>({ expanded: false, queryString: "", tsv: "" });
  const [queryResult, setQueryResult] = useState<string | null>(null);
  const [cypherResult, setCypherResult] = useState<any[]>([]);
  const [userInput, setUserInput] = useState<string>('');
  const [loading, setLoading] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);
  const [fragments, setFragments] = useState<any>(null);
  const containerRef = useRef<HTMLDivElement | null>(null);

  useEffect(() => {
    if (!containerRef.current) return undefined;
    console.log("containerRef.current", containerRef.current);
    const config: NeovisConfig = {
      //encrypted: "ENCRYPTION_ON",
      //trust: "TRUST_SYSTEM_CA_SIGNED_CERTIFICATES",
      containerId: containerRef.current.id,
      neo4j: {
      serverUrl: "neo4j://be20d4fc.databases.neo4j.io",
      serverUser: "neo4j",
      serverPassword: "sz7lL8-kJT9q5e7jN-j6VGoaEJ4XEXNRgHgJJugMp0U",
      },
      visConfig: {
      nodes: {
        shape: 'circle',
      },
      edges: {
        arrows: {
        to: { enabled: true },
        },
      },
      },
      labels: {
      nodes: {
        label: "Name",
      },
      },
      relationships: {
      CONNECTED: {},
      },
      initialCypher: "MATCH (w:IfcWindow) RETURN w",
    };

    const viz = new NeoVis(config);

    // Render the graph
    //viz.render();

    // Optional: Add event listeners
    viz.registerOnEvent("completed" as any, () => {
      console.log("Graph rendering completed!");
    });
    // Cleanup on component unmount
    return () => {
      viz.clearNetwork();
    };
  }, []);


 
  useEffect(() => {
    BUI.Manager.init();
    
    // Three.js World anf ifc model rendering
    const components = new OBC.Components();
    
    const container = document.getElementById("container")!;
    container
    if (container.getElementsByTagName("canvas").length > 0) {
      container.removeChild(container.getElementsByTagName("canvas")[0]);
    }
    container.style.width = "70vw";
    container.style.height = "70vh";
    container.style.margin = "auto";
    container.style.marginTop = "50px";

    const worlds = components.get(OBC.Worlds);

    const viewport = document.createElement("bim-viewport");
    viewport.name = "viewer";
    
    const world = worlds.create<
      OBC.SimpleScene,
      OBC.SimpleCamera,
      OBC.SimpleRenderer
    >();
    
    world.scene = new OBC.SimpleScene(components);
    world.renderer = new OBC.SimpleRenderer(components, container);
    world.camera = new OBC.SimpleCamera(components);
    
    components.init();
    
    world.camera.controls.setLookAt(12, 6, 8, 0, 0, -10);
    
    world.scene.setup();
    

    const grids = components.get(OBC.Grids);
    grids.create(world);

  

    world.scene.three.background = null;

    const fragments = components.get(OBC.FragmentsManager); 
    const fragmentIfcLoader = components.get(OBC.IfcLoader);
    
    //world.scene.three.background = 'hsl(0, 100%, 50%)';

    // C++ lib WASM fastens the computation
    fragmentIfcLoader.settings.wasm = {
         path: "https://unpkg.com/web-ifc@0.0.57/",
         absolute: true,
       };

    // exclude categories that we don't want to convert to fragments
    const excludedCats = [
        WEBIFC.IFCTENDONANCHOR,
        WEBIFC.IFCREINFORCINGBAR,
        WEBIFC.IFCREINFORCINGELEMENT,
      ];

      for (const cat of excludedCats) {
        fragmentIfcLoader.settings.excludedCategories.add(cat);
      }

    fragmentIfcLoader.settings.webIfc.COORDINATE_TO_ORIGIN = true;

    const ifcLoader = components.get(OBC.IfcLoader);
    ifcLoader.setup();


    const fragmentsManager = components.get(OBC.FragmentsManager);
    fragmentsManager.onFragmentsLoaded.add((model) => {
      if (world.scene) world.scene.three.add(model);

      const indexer = components.get(OBC.IfcRelationsIndexer);
      indexer.process(model);

    });
    const idmap = fragmentsManager.guidToFragmentIdMap("1s5utE$rDDfRKgzV6jUJUn");
    console.log("idmap: ", idmap);
    


    const [modelsList] = CUI.tables.modelsList({
      components,
      tags: { schema: true, viewDefinition: false },
      actions: { download: false },
    });

    // JSON exporter
    const exporter = components.get(OBC.IfcJsonExporter);

    const webIfc = new WEBIFC.IfcAPI();
    webIfc.SetWasmPath("https://unpkg.com/web-ifc@0.0.57/", true);
    webIfc.Init();

    async function _loadIfc(buffer: Uint8Array) {
      const model = await fragmentIfcLoader.load(buffer);
      world.scene.three.add(model);
      
      // Properties table section
      const indexer = components.get(OBC.IfcRelationsIndexer);
      indexer.process(model);
    }

    // Functionalities for panel sections
    
    const [propertiesTable, updatePropertiesTable] = CUI.tables.elementProperties({
      components,
      fragmentIdMap: {},
    });

    propertiesTable.preserveStructureOnFilter = true;
    propertiesTable.indentationInText = false;

    const highlighter = components.get(OBCF.Highlighter);
    highlighter.setup({ world });

  


    highlighter.events.select.onHighlight.add((fragmentIdMap) => {
      updatePropertiesTable({ fragmentIdMap });
    });


    highlighter.events.select.onClear.add(() =>
      updatePropertiesTable({ fragmentIdMap: {} }),
    );


    function download(file: File) {
      const link = document.createElement("a");
      link.href = URL.createObjectURL(file);
      link.download = file.name;
      document.body.appendChild(link);
      link.click();
      link.remove();
    }


    async function exportFragments() {
      if (!fragments.groups.size) {
        return;
      }
      const group = Array.from(fragments.groups.values())[0];
      const data = fragments.export(group);
      download(new File([new Blob([data])], "imported.frag"));
    
      const properties = group.getLocalProperties();
      if (properties) {
        download(new File([JSON.stringify(properties)], "imported.json"));
      }
    }

    function disposeFragments() {
      fragments.dispose();
    }


  const propertiesPanel = BUI.Component.create(() => {
    const onTextInput = (e: Event) => {
      const input = e.target as BUI.TextInput;
      propertiesTable.queryString = input.value !== "" ? input.value : null;
    };

  
    const expandTable = (e: Event) => {
      const button = e.target as BUI.Button;
      propertiesTable.expanded = !propertiesTable.expanded;
      button.label = propertiesTable.expanded ? "Collapse" : "Expand";
    };
  
    const copyAsTSV = async () => {
      await navigator.clipboard.writeText(propertiesTable.tsv);
    };

    return BUI.html`
        <bim-panel label="Properties" class="options-menu" style="position: absolute; top: 85rem; left: 80rem;>
          <bim-panel-section label="Element Data">
            <div style="display: flex; gap: 0.5rem;">
              <bim-button @click=${expandTable} label=${propertiesTable.expanded ? "Collapse" : "Expand"}></bim-button> 
               
            </div> 
            <bim-text-input @input=${onTextInput} placeholder="Search Property" debounce="250"></bim-text-input>
            ${propertiesTable}
          </bim-panel-section>
        </bim-panel>
      `; });
    const app = document.createElement("bim-grid");
    app.layouts = {
      main: {
        template: `
        "propertiesPanel viewport"
        /25rem 1fr
        `,
        elements: { propertiesPanel, container },
      },
    };
    

    app.layout = "main";
    document.body.append(app);


  const panel = BUI.Component.create<BUI.PanelSection>(() => {
    const [loadIfcBtn] = CUI.buttons.loadIfc({ components });

    const onglobalIdInput = (e: Event) => {
      const input = e.target as BUI.TextInput;
      const globalId = input.value;

      if (globalId) {
        // Assuming loadIfcBtn has a method to handle globalId
        console.log("globalId: ", globalId);
        const idmap = fragmentsManager.guidToFragmentIdMap(globalId);
        updatePropertiesTable({ fragmentIdMap: idmap });

      }
    }
    
    return BUI.html`
    <bim-panel active label="IFC Loader" class="options-menu" style="position: absolute; top: 4rem; right: 1rem; width: 15rem;">
      <bim-panel-section collapsed label="Controls">
      <bim-panel-section style="padding-top: 12px;">
      
        <bim-button label="Load IFC"
          @click="${() => {
            "_loadIfc();"
            }}">
            </bim-button>  
            <bim-panel-section label="Importing">
            ${loadIfcBtn} 
            
            </bim-panel-section>
            <bim-panel-section icon="mage:box-3d-fill" label="Loaded Models">
            ${modelsList}
            </bim-panel-section>
            <bim-text-input @input=${onglobalIdInput} placeholder="Global Id..." debounce="250"></bim-text-input>
            <bim-button label="Send Global Id"
            @click="${(e: Event) => {
              onglobalIdInput(e);
            }}">
            </bim-button>
            <bim-button label="Export fragments"
            @click="${() => {
          exportFragments();
        }}">
        </bim-button>  
      
        <bim-button label="Dispose fragments"
        @click="${() => {
          disposeFragments();
        }}">
        </bim-button>
      
      </bim-panel-section>
        <bim-panel-section style="padding-top: 10px;">
          <bim-button 
            label="Export properties JSON" 
            @click="${async () => {
              const exported = await exporter.export(webIfc, 1);
              const serialized = JSON.stringify(exported);
              const file = new File([new Blob([serialized])], "properties.json");
              const url = URL.createObjectURL(file);
              const link = document.createElement("a");
              link.download = "properties.json";
              link.href = url;
              link.click();
              URL.revokeObjectURL(url);
              link.remove();
            }}">  
          </bim-button>  
        </bim-panel-section>
      </bim-panel>
    </bim-panel>
    `;
  });

    document.body.append(panel);});


    const handleSend = () => {
      const inputElement = document.querySelector('input[type="text"]') as HTMLInputElement;
      if (!inputElement) return;
  
      const userInput = inputElement.value.trim();
      if (!userInput) return;
  
      setLoading(true);
      setError(null);
      setQueryResult(null);
      const saveIfcFile = async (data: string) => {
        const fileName = `userInput_${Date.now()}.ifc`;
        const filePath = `oxide/xeokit-bim-viewer/app/data/projects/rawModel/${fileName}`;
        const file = new File([data], fileName, { type: 'application/octet-stream' });

        try {
            const checkResponse = await fetch('/api/checkIfcFile', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({ filePath: `${filePath}.ifc` }),
            });

          const { exists } = await checkResponse.json();

          if (exists) {
        console.log('IFC file already exists');
        return;
          }

          const response = await fetch('/api/saveIfcFile', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ filePath, fileContent: await file.text() }),
          });

          if (!response.ok) {
        throw new Error('Failed to save IFC file');
          }

          console.log('IFC file saved successfully');
        } catch (error) {
          console.error('Error saving IFC file:', error);
        }
      };

      try{
        console.log("Not sending the ifc file the database for now...");
        //saveIfcFile(userInput);
      } catch (error) {
        console.error('Error saving IFC file:', error);
      }

        
  
      fetch('/api/runPython', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ userInput }),
      })
        .then((response) => response.json())
        .then((data) => {
          console.log('Query result:', data.result);
          setQueryResult(data.result); // Save response data
          setLoading(false);
        })
        .catch((err) => {
          console.error('Error fetching query result:', err);
          setError('Failed to fetch query result');
          setLoading(false);
        });
  
      inputElement.value = '';
    };



  return (
    <div>
      <div style={{background: "#fff"}}>
        <h1>Graph Visualization</h1>      
        <div
          id="graph-container"
          ref={containerRef}
          style={{ width: "50%", height: "40vh", border: "1px solid #ccc", backgroundColor: "#fff" }}
        ></div>
      </div>
      <div className="mb-12 mt-28 sm:mt-40 flex flex-col items-center justify-center">
        <div id="container" style={{ width: "10vw", height: "10vh", marginTop: "20px" }}></div>
      </div>
      <div className="mb-12 mt-28 sm:mt-40 flex flex-col items-center justify-center" style={{ marginTop: "200px", marginBottom: "350px" }}>
        <p className= "mt-5 max-w-prose text-zinc-700 sm:text-lg">  
          You can query BIM data from below.
        </p>
        <div className="chatbox-container" style={{ width: "600px", marginBottom: "100px", marginLeft: "10px" }}>
          <div className="chatbox-messages p-2 border border-gray-300 rounded-md" style={{ height: "300px", overflowY: "scroll" }}>
            {loading && <p>Loading...</p>}
            {error && <p style={{ color: 'red' }}>{error}</p>}
            {queryResult && <pre>{queryResult}</pre>}
          </div>
          <div className="chatbox-input mt-2 flex items-center space-x-2">
            <Input 
              type="text" 
              placeholder="Enter text here..." 
              className="p-2 border border-gray-300 rounded-md flex-grow"
            />
            <button 
              className="p-2 bg-blue-600 text-white rounded-md hover:bg-blue-700"
              onClick={() => {
              handleSend();
              }}
            >
              Send
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}


{/*


  onClick={() => {
              const inputElement = document.querySelector('input[type="text"]') as HTMLInputElement;
              if (inputElement) {
              const userInput = inputElement.value;
              console.log(userInput);
              sendInput(userInput);
              //sendQuery(userInput);
              // You can add more logic here to handle the user input
              inputElement.value = "";
              }
            }}





      <div style={{background: "#fff"}}>
        <h1>Graph Visualization</h1>
        <div id="container" style={{ width: "80vw", height: "80vh" }}></div>       <div
          id="graph-container"
          ref={containerRef}
          style={{ width: "100%", height: "80vh", border: "1px solid #ccc", backgroundColor: "#fff" }}
        ></div>

      
      
      </div>



    const containerRef = useRef<HTMLDivElement | null>(null);

  useEffect(() => {
    if (!containerRef.current) return undefined;

    const config = {
      encrypted:"ENCRYPTION_ON",
      trust: "TRUST_SYSTEM_CA_SIGNED_CERTIFICATES",
      containerId: containerRef.current.id,
     neo4j: {
         serverUrl: "neo4j://be20d4fc.databases.neo4j.io",
         serverUser: "neo4j",
         serverPassword: "sz7lL8-kJT9q5e7jN-j6VGoaEJ4XEXNRgHgJJugMp0U",
     },
     /*visConfig: {
      nodes: {
          shape: 'circle',
      },
      edges: {
          arrows: {
              to: {enabled: true}
                }
            },
        },
        labels: {
            Character: {
                label: 'any',
                [NeoVis.NEOVIS_ADVANCED_CONFIG]: {
                    cypher: {
                        value: "MATCH (n) WHERE id(n) = $id RETURN n.size"
                    },
                    function: {
                        title: (node: any) => {
                            return `Node ID: ${node.id}`;
                        }
                    },
                }
            }
        },
        relationships: {
            INTERACTS: {
                value: 'all',
                [NeoVis.NEOVIS_ADVANCED_CONFIG]: {
                    function: {
                        title: (edge: any) => {
                            return `Edge from ${edge.from} to ${edge.to}`;
                        }
                    },
                }
            }
        },
        initialCypher: 'MATCH (n)-[r]->(m) RETURN n,r,m'
};


      labels: {
        nodes: {
          label: "any",
          size: "pagerank",
        },
      },
      relationships: {
        CONNECTED: {},
      },
      initialCypher: "MATCH (n)-[r]->(m) RETURN n, r, m;",
    };

    const viz = new NeoVis(config);

    // Render the graph
    //viz.render();

    // Optional: Add event listeners
    viz.registerOnEvent("completed" as any, () => {
      console.log("Graph rendering completed!");
    });
    // Cleanup on component unmount
    return () => {
      viz.clearNetwork();
    };
  }, []);

  








  
  
  
  */ }