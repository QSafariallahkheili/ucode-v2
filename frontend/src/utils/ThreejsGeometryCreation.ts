import type { BoundingBox } from "@/store/modules/aoi";
import type { Feature, FeatureCollection, Geometry, Position, Properties } from "@turf/turf";
import maplibregl, { Map, MercatorCoordinate, type Coordinates, type LngLatLike } from "maplibre-gl";
import { BufferGeometry, DoubleSide, Vector2, Vector3 } from "three";
import * as THREE from "three";
import { GLTFLoader } from "three/examples/jsm/loaders/GLTFLoader.js";
import { LineGeometry } from "three/examples/jsm/lines/LineGeometry.js";
import { Line2 } from 'three/examples/jsm/lines/Line2.js';
import { LineMaterial } from 'three/examples/jsm/lines/LineMaterial.js';
import * as BufferGeometryUtils from 'three/examples/jsm/utils/BufferGeometryUtils.js'
import { CSS2DObject } from 'three/examples/jsm/renderers/CSS2DRenderer'

type TransformationWrapper = {
  position: number[];
  rotation: number;
  scale: number;
  userData?: { name: string };
};

type Mesh = {
  geometry: BufferGeometry;
  material: [];
};
export interface THREEGeoSettings {
  scene: THREE.Scene,
  bbox: BoundingBox,
  geoJson: FeatureCollection,
  color: string | string[],
  height: number,
  extrude: number,
  textureURL?: string
}

export function addPolygonsFromCoordsAr(settings: THREEGeoSettings): void {
  if (settings.geoJson.features == null) {
    console.error("No Data in GeoJson")
    return
  }
  let polygeom = new THREE.BufferGeometry()
  //let shapes: THREE.Shape[] =[]
  // console.log(settings.scene)
  let geoms: THREE.BufferGeometry[][] = settings.color instanceof Array ? [[], [], []] : [[]]
  if (settings.color instanceof Array) {
    geoms = createGeometryForBuildings(settings)
  }
  else {
    settings.geoJson.features.forEach((feature: Feature) => {
      if (feature.geometry.type !== "Polygon" || feature.geometry.coordinates.length == 0) {
        return
      }
      let geometry: BufferGeometry

      if (settings.extrude == 0) {
        geometry = new THREE.ShapeGeometry(createSinglePolygon(feature, settings.bbox), 0);
        geoms[0].push(geometry)
      }
      else {
        const extrudeSettings = {
          steps: 1,
          depth: settings.extrude,
          bevelEnabled: false,
          bevelThickness: 0,
          bevelSize: 0,
          bevelOffset: 0,
          bevelSegments: 1
        };
        geometry = new THREE.ExtrudeGeometry(createSinglePolygon(feature, settings.bbox), extrudeSettings)
        geoms[0].push(geometry)
      }
      geometry.rotateX(Math.PI / 2)
    })
  }
  // console.log(geoms)
  geoms.forEach((geom, index) => {
    polygeom = BufferGeometryUtils.mergeBufferGeometries(geom)
    let texture
    if (settings.textureURL) {
      texture = new THREE.TextureLoader().load(settings.textureURL);
      texture.wrapS = texture.wrapT = THREE.RepeatWrapping;
      texture.offset.set(0, 0);
      texture.repeat.set(0.2, 0.2);
    }
    let material = new THREE.MeshStandardMaterial({ color: geoms.length == 1 ? settings.color : settings.color[index], side: DoubleSide, roughness: 1, map: settings.textureURL ? texture : null })
    const mesh = new THREE.Mesh(polygeom, material);
    if (settings.extrude != .99) {
      mesh.translateY(settings.extrude)
    }
    settings.scene.add(mesh)
  })

}

export function addGeoOnPointsToThreejsScene(
  scene: THREE.Scene,
  geoJson: any,
  glbModel: string,
  bbox: BoundingBox,
  hasRandomSize?: number[],
  hasRandomRot?: boolean
): void {
  //console.log(scene);

  // use the three.js GLTF loader to add the 3D model to the three.js scene
  const loader = new GLTFLoader();
  loader.crossOrigin = "true";

  loader.load(
    glbModel,
    (gltf) => {
      const currentMeshes = getAllMeshes(gltf.scene);
      const localCoordinates = generateLocalCoordinates(
        geoJson,
        bbox,
        hasRandomSize
      );
      let raycaster = new THREE.Raycaster();
      raycaster.near = -1;
      raycaster.far = 1e6;

      localCoordinates.map(c => {
        if (c.position[1] == 0 && glbModel.startsWith('poiIcons')) {
          let dir = new THREE.Vector3(0, -1, 0)
          let origin = new THREE.Vector3(c.position[2], 1000, c.position[0])
          raycaster.set(origin, dir)
          let intersects = raycaster.intersectObjects(scene.children, true)
          if (intersects.length > 0) {
            c.position[1] = intersects[0].point.y
          }
        }
      })
      if (glbModel.startsWith('poiIcons')) {
        localCoordinates.map(coordinates => {
          let instance = gltf.scene.clone();
          instance.position.set(coordinates.position[2], coordinates.position[1], coordinates.position[0])
          instance.scale.set(coordinates.scale, coordinates.scale, coordinates.scale)
          instance.setRotationFromEuler(new THREE.Euler(0, coordinates.rotation, 0, "XYZ"))
          if (coordinates.userData?.name) {
            instance.userData = coordinates.userData
          }
          // console.log(instance)
          scene.add(instance);
          // console.log('Placed POI(' + glbModel + ') at: ' + instance.position.toArray())
          // console.log(coordinates.position)

        })
      }
      else {
        const clusters = createGeoInstances(
          localCoordinates,
          currentMeshes,
          hasRandomSize,
          hasRandomRot
        );
        clusters.forEach((cluster) => scene.add(cluster));
      }
    }
  );
}
function worldUnitMultiplator(bbox: BoundingBox) {
  let wrapperCords = localCordsFromWorldCords(maplibregl.LngLat.convert([bbox.xmin, bbox.ymin]), 0);
  console.log(1 / wrapperCords.meterInMercatorCoordinateUnits())
}
function worldPointInRelativeCoord(LngLatPoint: LngLatLike, bbox: BoundingBox) {
  let wrapperCords = localCordsFromWorldCords(maplibregl.LngLat.convert([bbox.xmin, bbox.ymin]), 0);
  let objectCords = localCordsFromWorldCords(LngLatPoint, 0);

  const relativePosition: THREE.Vector3 = new THREE.Vector3(

    ((wrapperCords.y - objectCords.y) * 1) / wrapperCords.meterInMercatorCoordinateUnits(),
    0,
    ((objectCords.x - wrapperCords.x) * 1) / wrapperCords.meterInMercatorCoordinateUnits()

  );
  // const relativePosition: THREE.Vector3 = new THREE.Vector3(



  //   (( objectCords.x- wrapperCords.x) * 1) / wrapperCords.meterInMercatorCoordinateUnits(),
  //   ((wrapperCords.y - objectCords.y) * 1) / wrapperCords.meterInMercatorCoordinateUnits(),
  //   0,

  // );
  return relativePosition
}
function getAllMeshes(scene: THREE.Group): THREE.Mesh[] {
  const meshes: THREE.Mesh[] = [];

  const extractMesh = (node: THREE.Object3D) => {

    if (node instanceof THREE.Mesh) {
      meshes.push(node);
    } else if (node instanceof THREE.Group) {
      node.children.forEach((child) => extractMesh(child));
    }
  };
  extractMesh(scene);
  return meshes;
}

function createGeoInstances(
  localSceneCoordinates: TransformationWrapper[],
  currentMeshes: Mesh[],
  hasRandomSize?: number[],
  hasRandomRot = false
): THREE.InstancedMesh[] {
  return currentMeshes.map((mesh) => {
    return createMeshInstance(
      mesh.geometry,
      mesh.material,
      localSceneCoordinates,
      hasRandomSize,
      hasRandomRot
    );
  });
}

function createMeshInstance(
  mesh: BufferGeometry,
  material: [],
  localSceneCoordinates: TransformationWrapper[],
  hasRandomSize: number[] | undefined,
  hasRandomRot: boolean
) {
  const instance = new THREE.InstancedMesh(
    mesh,
    material,
    localSceneCoordinates.length
  );
  const instanceDataAttribute = new THREE.InstancedBufferAttribute(new Float32Array(localSceneCoordinates.length), 1);
  localSceneCoordinates.forEach((localSceneCoordinate, index) => {
    let scale = new THREE.Vector3(1, 1, 1);
    let rotation = new THREE.Quaternion();
    let position = new THREE.Vector3(
      localSceneCoordinate.position[2],
      localSceneCoordinate.position[1],
      localSceneCoordinate.position[0]
    );

    if (hasRandomSize !== undefined) {
      scale = new THREE.Vector3(
        localSceneCoordinate.scale,
        localSceneCoordinate.scale,
        localSceneCoordinate.scale
      );
    }
    if (hasRandomRot) {
      let rot = localSceneCoordinate.rotation;
      let eulerRot = new THREE.Euler(0, rot, 0, "XYZ");
      rotation = rotation.setFromEuler(eulerRot);
    }
    if (localSceneCoordinate.userData?.name) {
      instanceDataAttribute.setX(index, addString(localSceneCoordinate.userData?.name))
    }

    const matrix = new THREE.Matrix4();
    matrix.compose(position, rotation, scale);
    instance.setMatrixAt(index, matrix);
  });
  instance.geometry.setAttribute('userData', instanceDataAttribute);
  return instance;
}
const stringToHash: { [key: string]: number } = {}; // object to store hash values of strings
const hashToString: { [key: string]: string } = {}; // object to store strings corresponding to hash values

function hashString(str: string) {
  let hash = 0;
  for (let i = 0; i < str.length; i++) {
    hash += str.charCodeAt(i);
  }
  return hash;
}
function addString(str: string) {
  const hash = hashString(str);
  stringToHash[str] = hash;
  hashToString[hash] = str;
  return hash;
}
export function getString(hash: number) {
  return hashToString[hash];
}
function encodeStringAsFloat(str: string | undefined) {
  if (str) {
    let float = 0;
    for (let i = 0; i < str.length; i++) {
      const charCode = str.charCodeAt(i);
      const exponent = 3 - i;
      float += (charCode / 255) * Math.pow(10, exponent);
    }
    return float;
  }
  else { return 0 }
}

function generateLocalCoordinates(
  _geoJson: { features: { geometry: { coordinates: [number, number] }[], properties: { estimatedheight: number, amenity_name?: string } }[] } | null,
  bbox: BoundingBox,
  hasRandomSize?: number[]
): TransformationWrapper[] {
  const localSceneCoordinates: TransformationWrapper[] = [];
  if (_geoJson != null) {
    for (let index = 0; index < _geoJson.features.length; index++) {
      const element = _geoJson.features[index].geometry.coordinates;

      let rot = getRndNumber(0, Math.PI / 2);
      let scl = getRndNumber(
        hasRandomSize ? hasRandomSize[0] : 1,
        hasRandomSize ? hasRandomSize[1] : 1
      );
      let cords = localCordsFromWorldCords(
        maplibregl.LngLat.convert([bbox.xmin, bbox.ymin]),
        _geoJson.features[index].properties.estimatedheight || 0
      );
      let localPos = {
        position: [
          ((localCordsFromWorldCords(element, _geoJson.features[index].properties.estimatedheight || 0).x - cords.x) * 1) /
          cords.meterInMercatorCoordinateUnits(),
          _geoJson.features[index].properties.estimatedheight || 0,
          ((cords.y - localCordsFromWorldCords(element, _geoJson.features[index].properties.estimatedheight || 0).y) * 1) /
          cords.meterInMercatorCoordinateUnits(),
        ],
        rotation: rot,
        scale: scl,
        userData: { 'name': _geoJson.features[index].properties.amenity_name }
      };
      localSceneCoordinates.push(localPos);
    }
  }
  return localSceneCoordinates;
}

function getRndNumber(min: number, max: number): number {
  return Math.random() * (max - min) + min;
}

export function localCordsFromWorldCords(
  worldCords: LngLatLike,
  height: number
): MercatorCoordinate {
  return maplibregl.MercatorCoordinate.fromLngLat(worldCords, height);
}
function createSinglePolygon(feature: Feature<any>, bbox: BoundingBox) {
  const vertAr: THREE.Vector2[] = []
  feature.geometry.coordinates[0].forEach((coord: Position) => {
    let pos: THREE.Vector3 = worldPointInRelativeCoord(new maplibregl.LngLat(coord[0], coord[1]), bbox)
    vertAr.push(new THREE.Vector2(pos.x, pos.z))
    // console.count("loop")
  })
  const shape = new THREE.Shape(vertAr);
  //Create holes in geometry
  if (feature.geometry.coordinates.length > 1) {
    for (let index = 1; index < feature.geometry.coordinates.length; index++) {

      let pathPoints: THREE.Vector2[] = []
      feature.geometry.coordinates[index].forEach((coord: Position) => {
        let pos: THREE.Vector3 = worldPointInRelativeCoord(new maplibregl.LngLat(coord[0], coord[1]), bbox)// console.log(pos)
        pathPoints.push(new THREE.Vector2(pos.x, pos.z))
      })
      let path = new THREE.Path(pathPoints)
      shape.holes[index - 1] = path
    }
  }
  return shape
}

function createGeometryForBuildings(settings: THREEGeoSettings) {
  let geoms: THREE.BufferGeometry[][] = [[], [], []]
  settings.geoJson.features.forEach((feature: Feature) => {
    if (feature.geometry.type !== "Polygon" || feature.geometry.coordinates.length == 0) {
      return
    }
    const extrudeSettings = {
      steps: 1,
      depth: feature.properties?.estimatedheight,
      bevelEnabled: true,
      bevelThickness: .2,
      bevelSize: .2,
      bevelOffset: 0,
      bevelSegments: 1
    };

    let geometry = new THREE.ExtrudeGeometry(createSinglePolygon(feature, settings.bbox), extrudeSettings)
    geometry.translate(0, 0, -feature.properties?.estimatedheight)
    geometry.rotateX(Math.PI / 2)
    const randomColoreFromColorPalette = () => {
      const lengthColors = settings.color.length;
      return settings.color[Math.floor(Math.random() * lengthColors)];
    }
    let color = randomColoreFromColorPalette()
    for (let index = 0; index < settings.color.length; index++) {
      if (color == settings.color[index]) {
        geoms[index].push(geometry)
      }
    }
  })
  return geoms
}

export function addLineFromCoordsAr(settings: THREEGeoSettings): void {//Lines not working due to Camera not being moved
  // const material = new THREE.LineBasicMaterial({ color: 0xffffff });
  let matLine = new LineMaterial({

    color: 0xffffff,
    linewidth: 1, // in world units with size attenuation, pixels otherwise
    worldUnits: true,
    vertexColors: false,

    resolution: new Vector2(1, 1), // to be set by renderer, eventually
    dashed: true,
    gapSize: 1,
    dashSize: 3,
    alphaToCoverage: true,
  });

  const material = new THREE.LineDashedMaterial({
    color: settings.color,
    linewidth: 10,
    scale: 1,
    dashSize: 5,
    gapSize: 2,
  });
  // let geometry: BufferGeometry = new THREE.BufferGeometry()
  matLine.side = THREE.DoubleSide
  settings.geoJson.features.forEach((feature: Feature) => {
    const points: number[] = []
    feature.geometry.coordinates.forEach((coord: Position) => {
      let point = worldPointInRelativeCoord(new maplibregl.LngLat(coord[0], coord[1]), settings.bbox)


      points.push(point.x, point.y, point.z)
      // console.log(worldPointInRelativeCoord(new maplibregl.LngLat(coord[0], coord[1]), settings.bbox))
    })
    // console.log(points)
    //geometry = new THREE.BufferGeometry().setFromPoints(points);
    const lineGeo = new LineGeometry();
    lineGeo.setPositions(points);

    // lineGeo.normalizeNormals();
    // debugger
    // lineGeo.computeVertexNormals();
    // lineGeo.rotateX(Math.PI/2)
    const line = new Line2(lineGeo, matLine);
    line.computeLineDistances()
    line.updateMorphTargets()
    settings.scene.add(line);
  })
}
export function addLineFromCoordsAr1(settings: THREEGeoSettings): void {//workaround until lines work
  let polygeoms: THREE.BufferGeometry[] = []
  // console.log(settings.geoJson)
  let material: THREE.MeshBasicMaterial = new THREE.MeshBasicMaterial()
  settings.geoJson.features.forEach((feature: Feature) => {
    material = new THREE.MeshBasicMaterial({ color: feature.properties?.color || settings.color });
    // console.log(material)

    if (feature.geometry.type == "MultiLineString") {
      polygeoms = []
      feature.geometry.coordinates.forEach((line) => { polygeoms.push(createLinesegments(line, settings)) })
      const geom = BufferGeometryUtils.mergeBufferGeometries(polygeoms)
      const mesh = new THREE.Mesh(geom, material)
      mesh.name = feature.properties?.route_name
      mesh.translateY(settings.height)
      settings.scene.add(mesh);
      // console.count("addMesh")
    }
    else if (feature.geometry.type == "LineString") {
      polygeoms.push(createLinesegments(feature.geometry.coordinates, settings))
    }
  })
  if (polygeoms.length > 0) {
    const geom = BufferGeometryUtils.mergeBufferGeometries(polygeoms)
    const mesh = new THREE.Mesh(geom, material)
    mesh.name = settings.geoJson.features[0].properties?.id
    mesh.translateY(settings.height)
    settings.scene.add(mesh);
  }
}

function createLinesegments(coords: any, settings: THREEGeoSettings) {
  const geoms: THREE.TubeGeometry[] = []
  let lastPoint: THREE.Vector3 = new THREE.Vector3(0, 0, 0)
  const curve0: THREE.CurvePath<THREE.Vector3> = new THREE.CurvePath()
  coords.forEach((coord: Position, index: number) => {
    let point = worldPointInRelativeCoord(new maplibregl.LngLat(coord[0], coord[1]), settings.bbox)

    if (index > 0) {

      let linecurve = new THREE.LineCurve3(lastPoint, point)
      linecurve.arcLengthDivisions = 1
      curve0.add(linecurve)
      geoms.push(new THREE.TubeGeometry(linecurve, 1, settings.extrude, 4, false))
    }
    lastPoint = point
  })
  if (coords.length - curve0.curves.length != 1) {
    console.error("not correct")
  }
  const polygeom = BufferGeometryUtils.mergeBufferGeometries(geoms)
  polygeom.translate(0, 0, settings.height)
  return polygeom
}
export function createCSS2DElement(intersect: THREE.Intersection, map: Map, scene: THREE.Scene) {
  const obj = getHighestParent(intersect.object)
  const hasNotCSS2DObject = () => {
    let hasNot = true
    scene.children.map(child => {
      if (child.isCSS2DObject !== undefined) {
        // hasNot = false
        scene.remove(child)
        return true
      }
    })
    return hasNot

  }
  if (obj instanceof THREE.Object3D && obj && hasNotCSS2DObject()) {
    const userData = obj.userData
    let text = userData.name;
    const textDiv = document.createElement('h1');
    textDiv.className = 'textDiv';
    textDiv.textContent = text;
    textDiv.style.backgroundColor = 'white';
    textDiv.style.borderRadius = '8px';
    textDiv.style.padding = '0.5rem';
    textDiv.style.textAlign = 'center';

    // create a CSS2DObject with the div element
    const textObject = new CSS2DObject(textDiv);
    // set the position of the CSS2DObject
    var box = new THREE.Box3().setFromObject(obj);
    let height = box.max.y
    textObject.position.copy(obj.position)
    textObject.position.add(new Vector3(0,height,0))
    
    // add the CSS2DObject to the scene
    scene.add(textObject);

    setTimeout(function () {
      scene.remove(textObject);
      map.triggerRepaint();
    }, 5000);

  }
}
function getHighestParent(obj: THREE.Object3D) {
  var parent = obj.parent;
  while (parent && parent.type !== "Scene") {
    obj = parent;
    parent = obj.parent;
  }
  return obj;
}