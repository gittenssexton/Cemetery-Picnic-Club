[out:json][timeout:180];
// Overinclusive discovery: 25-mile Pine Grove circle and Route 9 vicinity bbox.
// Final corridor inclusion requires a separately sourced Route 9 GeoJSON.
(
  nwr["landuse"="cemetery"](around:40234,42.20909,-72.19660);
  nwr["amenity"="grave_yard"](around:40234,42.20909,-72.19660);
  nwr["landuse"="cemetery"](42.20,-72.66,42.44,-72.15);
  nwr["amenity"="grave_yard"](42.20,-72.66,42.44,-72.15);
);
out center geom;