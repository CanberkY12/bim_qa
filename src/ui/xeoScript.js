// Import if using ES6 or bundlers
import {Viewer} from '@xeokit/xeokit-sdk/src/viewer/Viewer.js'



export function initializeViewer(viewerId) {

    // Create a new Viewer instance
    const viewer = new Viewer({
        canvasId: "viewer" // Match this to the ID of the HTML element you created
    });

    // Add a camera and scene to your viewer instance
    const camera = viewer.camera;
    const scene = viewer.scene;

    // Example loading a glTF model
    scene.loadIFC({
        src: "https://thatopen.github.io/engine_components/resources/small.ifc"  // URL to the 3D model
    }).then(() => {
        // Center and fit the model into the view
        viewer.cameraControl.fitToBounds();
    });

    // Add a section plane
    viewer.scene.addSectionPlane({
        pos: [0, 0, 0],  // Section position
        dir: [0, 1, 0]   // Section direction
    });

    viewer.scene.input.on("pick", function (hit) {
        if (hit) {
            console.log("Picked object ID:", hit.entity.id);
            // Perform actions with the picked object here
        }
    });

    viewer.cameraControl.setDefaultNavigationMode("orbit");
    viewer.scene.setBackgroundColor([0.9, 0.9, 0.9]); // light grey background

}

export default initializeViewer;
