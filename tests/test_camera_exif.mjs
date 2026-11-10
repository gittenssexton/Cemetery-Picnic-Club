// Node-only regression test for camera EXIF GPS exports.
// Does not access camera, network, browser GPS, storage, or live photos.
import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import { runInNewContext } from 'node:vm';

const code = readFileSync(new URL('../web/camera/exif.js', import.meta.url), 'utf8');
const context = { Uint8Array, ArrayBuffer, DataView, Math, Number };
runInNewContext(code, context);
const { addGPS } = context.CPCGeoTag;
assert.equal(typeof addGPS, 'function');

function inspect(bytes) {
  assert.equal(bytes[0], 255);
  assert.equal(bytes[1], 216);
  assert.equal(bytes[2], 255);
  assert.equal(bytes[3], 225);
  const length = bytes[4] * 256 + bytes[5];
  assert.equal(String.fromCharCode(...bytes.slice(6, 10)), 'Exif');
  const start = 12;
  const view = new DataView(bytes.buffer, bytes.byteOffset + start);
  const little = true;
  assert.equal(view.getUint16(2, little), 42);
  const gpsOffset = view.getUint32(18, little);
  assert.equal(view.getUint16(gpsOffset, little), 6);
  function entryAt(n) {
    const p = gpsOffset + 2 + n * 12;
    return { tag: view.getUint16(p, little),
      type: view.getUint16(p + 2, little),
      count: view.getUint32(p + 4, little),
      value: view.getUint32(p + 8, little),
      p };
  }
  function dms(entry) {
    const pos = entry.value;
    return Array.from({length: 3}, (_, i) =>
      view.getUint32(pos + i*8, little) / view.getUint32(pos + i*8 + 4, little)
    ).reduce((sum, n, i) => sum + n / [1, 60, 3600][i], 0);
  }
  const entries = Array.from({length: 6}, (_, i) => entryAt(i));
  assert.deepEqual(entries.map(x => x.tag), [0, 1, 2, 3, 4, 18]);
  const latSign = bytes[start + entries[1].p + 8] === 83 ? -1 : 1;
  const lonSign = bytes[start + entries[3].p + 8] === 87 ? -1 : 1;
  return { lat: latSign*dms(entries[2]), lon: lonSign*dms(entries[4]),
    originalOffset: 2 + 2 + length };
}

for (const [lat, lon] of [[42.20909,-72.19660], [-33.8688,151.2093], [0,0], [89.999,-179.999]]) {
  // Minimal JPEG SOI/EOI fixture. This checks EXIF structure and original byte retention,
  // not whether a phone camera provides a valid decoded photograph.
  const original = new Uint8Array([0xff,0xd8,0xff,0xd9]);
  const before = Uint8Array.from(original);
  const tagged = addGPS(original,lat,lon);
  assert.deepEqual(Array.from(original), Array.from(before), 'original JPEG mutated');
  const info = inspect(tagged);
  assert.ok(Math.abs(info.lat-lat) < 0.000001, 'latitude mismatch');
  assert.ok(Math.abs(info.lon-lon) < 0.000001, 'longitude mismatch');
  assert.deepEqual(Array.from(tagged.slice(info.originalOffset)),
    Array.from(original.slice(2)), 'original JPEG payload changed');
}
for (const [lat,lon] of [[91,0],[0,181],[NaN,0],[0,Infinity]]) {
  assert.throws(() => addGPS(new Uint8Array([255,216,255,217]), lat, lon));
}
assert.throws(() => addGPS(new Uint8Array([0,0]), 42, -72));
console.log('Camera EXIF GPS assertions passed; four coordinate fixtures and mutation checks');
