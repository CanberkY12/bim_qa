import * as WEBIFC from "web-ifc";
import * as BUI from "@thatopen/ui";
import Stats from "stats.js";
import * as OBC from "@thatopen/components";
import * as OBCF from "@thatopen/components-front";
import { FragmentsGroup } from "@thatopen/fragments";
import * as CUI from "C:/Users/berky/oxide/thatOpenSrc/engine_ui-components/packages/obc/src/components";


export function initializeOBC() {
    
    const container = document.getElementById("contamiantor");


    const components = new OBC.Components();
    
    const worlds = components.get(OBC.Worlds);

    const scene = components.SimpleScene
    const simpleCamera = components.SimpleCamera
    const simpleRenderer = components.SimpleRenderer

    const world = worlds.create({
        scene,
        camera: simpleCamera,
        renderer: simpleRenderer,
        container
    });
    components.init();
    
    world.scene = new OBC.SimpleScene(components);
    world.renderer = new OBC.SimpleRenderer(components, container);
    world.camera = new OBC.SimpleCamera(components);


    world.camera.controls.setLookAt(12, 6, 8, 0, 0, -10);

    world.scene.setup();

    const grids = components.get(OBC.Grids);
    grids.create(world);

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
  /*
    const ifcLoader = components.get(OBC.IfcLoader);
    ifcLoader.setup();
    const file = fetch(
      "https://thatopen.github.io/engine_ui-components/resources/small.ifc",
    );
    const buffer = file.arrayBuffer();
    const typedArray = new Uint8Array(buffer);
    const model = ifcLoader.load(typedArray);
    world.scene.three.add(model);
*/

    async function loadIfc() {
        const file = await fetch(
          //"https://thatopen.github.io/engine_components/resources/small.ifc",
        );
        
        const data = await file.arrayBuffer();
        const buffer = new Uint8Array(data);
        const model = await fragmentIfcLoader.load(buffer);
        model.name = "example";
        world.scene.three.add(model);



        const indexer = components.get(OBC.IfcRelationsIndexer);
        indexer.process(model);
    
    
        // properties table created
        const [propertiesTable, updatePropertiesTable] = CUI.tables.elementProperties({
          components,
          fragmentIdMap: {},
        });
        
        //Creating a panel to append the table
        propertiesTable.preserveStructureOnFilter = true;
        propertiesTable.indentationInText = false;
    
        highlighter.events.select.onHighlight.add((fragmentIdMap) => {
          updatePropertiesTable({ fragmentIdMap });
        });
        
        highlighter.events.select.onClear.add(() =>
          updatePropertiesTable({ fragmentIdMap: {} }),
        );
      }


    // Once you have your precious fragments, you might want to save them so that you don't need to open this IFC file each time your user gets into your app. Instead, the next time you can load the fragments directly.

    function download(file) {
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
    // Highlighter
    const highlighter = components.get(OBCF.Highlighter);
    highlighter.setup({ world });
    highlighter.zoomToSelection = true;

    // Load IFC

  loadIfc();
  return components;
}


export default initializeOBC;






