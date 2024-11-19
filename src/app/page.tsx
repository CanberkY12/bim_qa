"use client"
 
import { useState, useEffect, useRef } from 'react'
import { Input } from "@/components/ui/input"
import MaxWidthWrapper from "./components/MaxWidthWrapper";
import ClickComponent from "./components/ButtonReciever";
import { ArrowRight } from "lucide-react"
import { buttonVariants } from "@/components/ui/button";
import { LoginLink } from "@kinde-oss/kinde-auth-nextjs";
import { Html } from 'next/document';
import { initializeOBC } from "C:/Users/berky/oxide/src/ui/script.js";
import * as xeoScript from "C:/Users/berky/oxide/src/ui/xeoScript.js";
import * as BUI from "@thatopen/ui";

import PropertiesPanel from 'C:/Users/berky/oxide/src/ui/PropertiesPanel';
import { ElementPropertiesUI } from '../../thatOpenSrc/engine_ui-components/packages/obc/src/components/tables/ElementProperties/src/template';
import * as CUI from "C:/Users/berky/oxide/thatOpenSrc/engine_ui-components/packages/obc/src/components";

import * as WEBIFC from "web-ifc";


import * as OBC from "@thatopen/components";
import * as OBCF from "@thatopen/components-front";
import { FragmentsGroup } from "@thatopen/fragments";
import { viewport } from '../../thatOpenSrc/engine_ui-components/packages/obc/src/components/tables/ElementProperties/example';
import sendInput from "C:/Users/berky/oxide/src/app/llmGraphQL/promptreceiver.js"
import NeoVis, { NeovisConfig } from "neovis.js/dist/neovis.js";
//import * as lchain2cypher from 'C:/Users/berky/oxide/src/app/llmGraphQL/lchain2cypher.py';



export default function Home() {
  const [propertiesTable, setPropertiesTable] = useState<any>({ expanded: false, queryString: "", tsv: "" });
  const containerRef = useRef<HTMLDivElement | null>(null);

  useEffect(() => {
    if (!containerRef.current) return;

    const config = {
      encrypted:"ENCRYPTION_ON",
      trust: "TRUST_SYSTEM_CA_SIGNED_CERTIFICATES",
      containerId: containerRef.current.id,
     neo4j: {
         serverUrl: "neo4j://be20d4fc.databases.neo4j.io",
         serverUser: "neo4j",
         serverPassword: "sz7lL8-kJT9q5e7jN-j6VGoaEJ4XEXNRgHgJJugMp0U",
     },
      labels: {
        nodes: {
          label: "IFCTYPE",
          size: "pagerank",
        },
      },
      relationships: {
        CONNECTED: {},
      },
      initialCypher: "MATCH (n)-[r]->(m) RETURN n, r, m LIMIT 50",
    };

    const viz = new NeoVis(config);

    // Render the graph
    viz.render();

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
    //if (!container) {
    //  const newContainer = document.createElement("div");
    //  newContainer.id = "container";
    //  document.body.appendChild(newContainer);
    //}

    // Create a container for the canvas
    //const container = document.createElement("container");
    //container.style.width = "80vw";
    //container.style.height = "80vh";
    //document.body.append(container);

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
    
    /*viewport.addEventListener("resize", () => {
      world.renderer.resize();
      cameraComponent.updateAspect();
    });*/



    const grids = components.get(OBC.Grids);
    grids.create(world);

  

    world.scene.three.background = null;

    const fragments = components.get(OBC.FragmentsManager); 
    const fragmentIfcLoader = components.get(OBC.IfcLoader);
    
    //world.scene.three.background = 'hsl(0, 100%, 50%)';

    // C++ lib WASM fastens the computation
    fragmentIfcLoader.setup();

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


    // JSON exporter
    const exporter = components.get(OBC.IfcJsonExporter);

    const webIfc = new WEBIFC.IfcAPI();
    webIfc.SetWasmPath("https://unpkg.com/web-ifc@0.0.57/", true);
    webIfc.Init();


    async function _loadIfc() {
      const file = await fetch(
         "https://thatopen.github.io/engine_components/resources/small.ifc",
      );
      const data = await file.arrayBuffer();
      const buffer = new Uint8Array(data);
      const model = await fragmentIfcLoader.load(buffer);

      world.scene.three.add(model);
      
      // Properties table section
      const indexer = components.get(OBC.IfcRelationsIndexer);
      indexer.process(model);
    }


    /*async function loadIfc(importedIFC) {
      const file = await fetch(
        
      );
      console.log(file);
      const data = await file.arrayBuffer();
      const buffer = new Uint8Array(data);
      const model = await fragmentIfcLoader.load(buffer);

      world.scene.three.add(model);
      
      // Properties table section
      const indexer = components.get(OBC.IfcRelationsIndexer);
      indexer.process(model);
    }*/


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
          <bim-panel label="Properties" class="options-menu" style="position: absolute; top: 40rem; left: 1rem; width: 30rem;>
            <bim-panel-section label="Element Data">
              <div style="display: flex; gap: 0.5rem;">
                <bim-button @click=${expandTable} label=${propertiesTable.expanded ? "Collapse" : "Expand"}></bim-button> 
                <bim-button @click=${copyAsTSV} label="Copy as TSV"></bim-button> 
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
    
      return BUI.html`
      <bim-panel active label="IFC Loader" class="options-menu" style="position: absolute; top: 75rem; right: 1rem; width: 15rem;">
        <bim-panel-section collapsed label="Controls">
        <bim-panel-section style="padding-top: 12px;">
        
          <bim-button label="Load IFC"
            @click="${() => {
            _loadIfc();
            }}">
          </bim-button>  
          <bim-panel-section label="Importing">
            ${loadIfcBtn} 
            
          </bim-panel-section>
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

 
      `;
      });

      document.body.append(panel);});

      



  return (
    <div>
      <div style={{background: "#fff"}}>
        <h1>Graph Visualization</h1>
        <div
          id="graph-container"
          ref={containerRef}
          style={{ width: "100%", height: "80vh", border: "1px solid #ccc", backgroundColor: "#fff" }}
        ></div>
      </div>

      <div className="mb-12 mt-28 sm:mt-40 flex flex-col items-center justify-center">
        <div id="container" style={{ width: "90vw", height: "90vh", marginTop: "-160px"}}></div>
      </div>
      <div className="mb-12 mt-28 sm:mt-40 flex flex-col items-center justify-center" style={{ marginTop: "850px", marginBottom: "100px" }}>
        <p className= "mt-5 max-w-prose text-zinc-700 sm:text-lg">  
          You can query BIM data from below.
        </p>
        <div className="mt-5 flex items-center space-x-2" style ={{width: "600px"}}>

        <Input 
          type="text" 
          placeholder="Enter text here..." 
          className="p-2 border border-gray-300 rounded-md flex-grow"
        />

            <button 
            className="p-2 bg-blue-600 text-white rounded-md hover:bg-blue-700" 
            onClick={() => {
              const inputElement = document.querySelector('input[type="text"]') as HTMLInputElement;
              if (inputElement) {
              const userInput = inputElement.value;
              console.log(userInput);
              sendInput(userInput);
              // You can add more logic here to handle the user input
              inputElement.value = "";
              }
            }}

            >
            Send
            </button>
        </div>
      </div>
    </div>
  );
}


{/*      
<div className="mb-12 mt-28 sm:mt-40 flex flex-col items-center justify-center">
      <div className="mb-12 mt-28 sm:mt-40 flex flex-col items-center justify-center"/>
        <h1 className="max-w-4xl text-5xl font-bold md:text-6xl lg:text-6xl mt-12" style={{ marginTop: "-220px", marginBottom: "50px" }}>
          Welcome to LLM4BIM
        </h1>
  

        <p className= "mt-5 max-w-prose text-zinc-700 sm:text-lg" style={{ marginBottom: "25px" }}>  
          You can visualize your BIM model and query information here.
        </p>
          

        
        <p className= "mt-5 max-w-prose text-zinc-700 sm:text-lg">  
        You can query BIM data from below.
      </p>
      <div className="mt-5 flex items-center space-x-2" style={{ width: "50vw"}}>

      <Input 
        type="text" 
        placeholder="Enter text here" 
        className="p-2 border border-gray-300 rounded-md flex-grow"
      />

        <button 
          className="p-2 bg-blue-600 text-white rounded-md "
          onClick={() => {
            const inputElement = document.querySelector('input[type="text"]') as HTMLInputElement;
            if (inputElement) {
              const userInput = inputElement.value;
              console.log(userInput);
              sendInput(userInput);
              // You can add more logic here to handle the user input
              inputElement.value = "";
            }
          }}

        >
          Send
        </button>
      </div>
    </div>











              @click="${async () => {
                const input = document.createElement('input');
                input.type = 'file';
                input.accept = '.ifc';
                input.onchange = async (e) => {
                  const file = (e.target as HTMLInputElement).files?.[0];
                  await loadIfc(); // Call _loadIFC with selected file
                };
                input.click(); // Trigger the file input
              }}">
            
  
  
  <input 
            id="file-input"
            type="file"
            className="mt-5 p-2 border border-gray-300 rounded-md"
            @change="${(e: Event) => {
              const input = e.target as HTMLInputElement;
              if (input.files && input.files[0]) {
              const file = input.files[0];
              const reader = new FileReader();
              _loadIfc();
              };
              
              }
            }}"
            />
  
  
  
  
  <div id="container" style={{ width: "80vw", height: "60vh", marginTop: "5px" }}>
  
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
      download(new File([new Blob([data])], "small.frag"));
      
      const properties = group.getLocalProperties();
      if (properties) {
        download(new File([JSON.stringify(properties)], "small.json"));
      }
      }
    
      function disposeFragments() {
      fragments.dispose();
      }
  
  
  
  
  
  
  return BUI.html`
        <bim-panel label="Properties">
          <bim-panel-section label="Element Data">
            <div style="display: flex; gap: 0.5rem;">
               <bim-button @click=${expandTable} label=${propertiesTable.expanded ? "Collapse" : "Expand"}></bim-button>
              <bim-button @click=${copyAsTSV} label="Copy as TSV"></bim-button> 
            </div> 
            <bim-text-input @input=${onTextInput} placeholder="Search Property" debounce="250"></bim-text-input>
            ${propertiesTable}
          </bim-panel-section>
        </bim-panel>
      `;
    });


    document.body.append(panel);
    document.body.append(propertiesPanel);
 

    if (container) {
      container.appendChild(panel);
      container.appendChild(propertiesPanel);
    }
  
  
  const panel = BUI.Component.create<BUI.PanelSection>(() => {
      const [loadIfcBtn] = CUI.buttons.loadIfc({ components });
      return BUI.html`
      <bim-panel active label="IFC Loader" class="options-menu">
        <bim-panel-section collapsed label="Controls">
          <bim-panel-section label="Importing" style="padding-top: 12px;">
              
              ${loadIfcBtn}
          </bim-panel-section>      
        </bim-panel>
              `;
    });
  
  
  
  const script = document.createElement("script");
    script.src = "C:/Users/berky/oxide/src/ui/script.js";
    script.async = true;
    //document.body.appendChild(script);
    
  
  
  
  <script src="C:\Users\berky\oxide\src\ui\script.js"></script>

        <p className= "mt-5 max-w-prose text-zinc-700 sm:text-lg">  
        You can query BIM data from below.
      </p>
      <div className="mt-5 flex items-center space-x-2">

        <Input 
          type="text" 
          placeholder="Enter text here" 
          className="p-2 border border-gray-300 rounded-md flex-grow"
        />

        <button 
          className="p-2 bg-blue-600 text-white rounded-md"
          onClick={() => {
            const inputElement = document.querySelector('input[type="text"]') as HTMLInputElement;
            if (inputElement) {
              const userInput = inputElement.value;
              console.log(userInput);
              // You can add more logic here to handle the user input
            }
          }}
        >
          Send
        </button>
      </div>
       <input 
          id="file-input"
          type="file"
          className="mt-5 p-2 border border-gray-300 rounded-md"
        />
        <button 
            type = "button"
            className="p-2 bg-blue-600 text-white rounded-md"

            
          >
            Upload
          </button>
      </div>


*/}