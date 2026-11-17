// The map's projection: from longitude and latitude to the flat map, scaled so the world is one unit wide, x running east from the
// antimeridian and y south from the top of the world. The map files are written in it, so changing it means rebuilding them
// (node tools/map/build-map-geometry.ts); everything else follows the projection named here.

export type Projection = {
  name: string;
  // The world's height in map units (its width is 1).
  worldHeight: number;
  // Whether shapes far from the equator are drawn larger than they are, so their coasts can be simplified harder.
  enlargesHighLatitudes: boolean;
  project(longitude: number, latitude: number): [number, number];
  invert(x: number, y: number): [number, number];
};

// Equal Earth (Šavrič, Patterson and Jenny, 2018): every place at its true size, without Mercator's bloated north.
const [a1, a2, a3, a4] = [1.340264, -0.081106, 0.000893, 0.003796], m = Math.sqrt(3) / 2;
const equalEarthY = (theta: number) => theta * (a1 + a2 * theta ** 2 + theta ** 6 * (a3 + a4 * theta ** 2));
const equalEarthSlope = (theta: number) => a1 + 3 * a2 * theta ** 2 + theta ** 6 * (7 * a3 + 9 * a4 * theta ** 2);
const equalEarthXMax = 2 * Math.sqrt(3) * Math.PI / (3 * a1), equalEarthYMax = equalEarthY(Math.asin(m));
const equalEarth: Projection = {
  name: 'equal-earth',
  worldHeight: equalEarthYMax / equalEarthXMax,
  enlargesHighLatitudes: false,
  project(longitude, latitude) {
    const lambda = longitude * Math.PI / 180, theta = Math.asin(m * Math.sin(latitude * Math.PI / 180));
    const x = 2 * Math.sqrt(3) * lambda * Math.cos(theta) / (3 * equalEarthSlope(theta));
    return [(x / equalEarthXMax + 1) / 2, (equalEarthYMax - equalEarthY(theta)) / (2 * equalEarthXMax)];
  },
  invert(mapX, mapY) {
    const x = (mapX * 2 - 1) * equalEarthXMax, y = equalEarthYMax - mapY * 2 * equalEarthXMax;
    let theta = y / a1;
    for (let step = 0; step < 12; step++) theta -= (equalEarthY(theta) - y) / equalEarthSlope(theta);
    const longitude = 3 * x * equalEarthSlope(theta) / (2 * Math.sqrt(3) * Math.cos(theta)) * 180 / Math.PI;
    return [longitude, Math.asin(Math.max(-1, Math.min(1, Math.sin(theta) / m))) * 180 / Math.PI];
  },
};

// Cylindrical projections, turned 11° east as on Apple Prices so the world's edge falls in the Bering Strait. Each is given by
// how far north of the equator a latitude is drawn, in units of the world's width at the equator (2π), and its inverse.
const cylindricalEdge = -169, radians = Math.PI / 180;
function cylindrical(name: string, northOf: (phi: number) => number, latitudeAt: (north: number) => number, enlargesHighLatitudes = true): Projection {
  const top = northOf(85 * radians);
  return {
    name, enlargesHighLatitudes, worldHeight: 2 * top / (2 * Math.PI),
    project(longitude, latitude) {
      const phi = Math.max(-85, Math.min(85, latitude)) * radians;
      return [(longitude - cylindricalEdge) / 360, (top - northOf(phi)) / (2 * Math.PI)];
    },
    invert(x, y) {
      const longitude = x * 360 + cylindricalEdge;
      return [longitude > 180 ? longitude - 360 : longitude, latitudeAt(top - y * 2 * Math.PI) / radians];
    },
  };
}
const byNewton = (northOf: (phi: number) => number) => (north: number) => {
  let phi = north / 2;
  for (let step = 0; step < 30; step++) phi -= (northOf(phi) - north) / ((northOf(phi + 1e-6) - northOf(phi - 1e-6)) / 2e-6);
  return phi;
};

// Web Mercator, as on most zoomable maps: true shapes up close, the far north greatly enlarged.
const mercatorNorth = (phi: number) => Math.log(Math.tan(Math.PI / 4 + phi / 2));
const mercator = cylindrical('mercator-11e', mercatorNorth, north => 2 * Math.atan(Math.exp(north)) - Math.PI / 2);
// Miller: Mercator with the north swelling 40% less; Europe drawn a little flat.
const millerNorth = (phi: number) => 1.25 * Math.log(Math.tan(Math.PI / 4 + 0.4 * phi));
const miller = cylindrical('miller-11e', millerNorth, north => 2.5 * Math.atan(Math.exp(0.8 * north)) - 0.625 * Math.PI);
// Patterson (2014): the north smaller still.
const pattersonNorth = (phi: number) => 1.0148 * phi + 0.23185 * phi ** 5 - 0.14499 * phi ** 9 + 0.02406 * phi ** 13;
const patterson = cylindrical('patterson-11e', pattersonNorth, byNewton(pattersonNorth));
// Gall stereographic, standard parallels at 45°: half Mercator's swelling of the north, Europe and the US close to their true shape.
const gallNorth = (phi: number) => (1 + Math.SQRT1_2) * Math.tan(phi / 2) * Math.SQRT2;
const gall = cylindrical('gall-stereographic-11e', gallNorth, north => 2 * Math.atan(north / ((1 + Math.SQRT1_2) * Math.SQRT2)));

export const projections = { 'equal-earth': equalEarth, 'mercator-11e': mercator, 'miller-11e': miller, 'patterson-11e': patterson, 'gall-stereographic-11e': gall };
// Josh is choosing between Gall stereographic, Miller and Patterson; this line is the choice. The map files must then be rebuilt.
export const projection: Projection = gall;

// A longitude moved by whole turns so it falls on the map: the Aleutians and Chukotka west of the edge go to its far right.
// Shapes are moved whole, by their middle, so none is torn across the edge.
export const worldEdgeLongitude = projection === equalEarth ? -180 : cylindricalEdge;
export const onTheMap = (longitude: number) => (longitude < worldEdgeLongitude ? longitude + 360 : longitude);
export const projectPoint = (longitude: number, latitude: number) => projection.project(onTheMap(longitude), latitude);
