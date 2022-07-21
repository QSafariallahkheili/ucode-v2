import maplibregl from 'maplibre-gl'
import * as THREE from 'three'

export const CubeModel = (lng, lat, id)=> {
  const modelAltitude = 0;
  const modelRotate = [Math.PI / 2, 0, 0];
  const modelorigin = [lng, lat]
  const modelAsMercatorCoordinate = maplibregl.MercatorCoordinate.fromLngLat(
    modelorigin,
    modelAltitude
  );

  
  
 
  // transformation parameters to position, rotate and scale the 3D model onto the map
  const modelTransform = {
    translateX: modelAsMercatorCoordinate.x,
    translateY: modelAsMercatorCoordinate.y,
    translateZ: modelAsMercatorCoordinate.z,
    rotateX: modelRotate[0],
    rotateY: modelRotate[1],
    rotateZ: modelRotate[2],
    /* Since the 3D model is in real world meters, a scale transform needs to be
    * applied since the CustomLayerInterface expects units in MercatorCoordinates.
    */
    scale: modelAsMercatorCoordinate.meterInMercatorCoordinateUnits()
  };
 
  //const THREE = window.THREE;
 
  // configuration of the custom layer for a 3D model per the CustomLayerInterface
  const customLayer = {
    id: id,
    type: 'custom',
    renderingMode: '3d',
      onAdd: function (map, gl) {
        this.camera = new THREE.Camera();
        this.scene = new THREE.Scene();
 
        // create two three.js lights to illuminate the model
        const directionalLight = new THREE.DirectionalLight(0xffffff);
        directionalLight.position.set(0, -70, 100).normalize();
        this.scene.add(directionalLight);
 
        const directionalLight2 = new THREE.DirectionalLight(0xffffff);
        directionalLight2.position.set(0, 70, 100).normalize();
        this.scene.add(directionalLight2);
 

  
        const geometry = new THREE.BoxBufferGeometry( 100, 100, 100 );
      
      

      

        const loader = new THREE.TextureLoader();

      
       
        let material = new THREE.MeshBasicMaterial( { color: 0x00ff00 } )
        const cube = new THREE.Mesh( geometry, material );
        
        console.log(cube.rotation.x, cube.rotation.y, cube.rotation.z)
        this.scene.add(cube);
        
        
        this.map = map;
 
        // use the Mapbox GL JS map canvas for three.js
        this.renderer = new THREE.WebGLRenderer({
          canvas: map.getCanvas(),
          context: gl,
          antialias: true
        });
 
        this.renderer.autoClear = false;
      },


      render: function (gl, matrix) {
        const rotationX = new THREE.Matrix4().makeRotationAxis(
          new THREE.Vector3(1, 0, 0),
          modelTransform.rotateX
        );
        const rotationY = new THREE.Matrix4().makeRotationAxis(
          new THREE.Vector3(0, 1, 0),
          modelTransform.rotateY
        );
        const rotationZ = new THREE.Matrix4().makeRotationAxis(
          new THREE.Vector3(0, 0, 1),
          modelTransform.rotateZ
        );
 
        const m = new THREE.Matrix4().fromArray(matrix);
        const l = new THREE.Matrix4()
        .makeTranslation(
          modelTransform.translateX,
          modelTransform.translateY,
          modelTransform.translateZ
        )
        .scale(
          new THREE.Vector3(
            modelTransform.scale*5,
            -modelTransform.scale*5,
            modelTransform.scale*5
          )
        )
        .multiply(rotationX)
        .multiply(rotationY)
        .multiply(rotationZ);
 
        this.camera.projectionMatrix = m.multiply(l);
        //this.renderer.state.reset();
        this.renderer.resetState();
        this.renderer.render(this.scene, this.camera);
        this.map.triggerRepaint();
      }
  };

  return (
    customLayer
  )
 
 

}