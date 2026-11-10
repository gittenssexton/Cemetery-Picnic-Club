import assert from 'node:assert/strict';
import { webcrypto } from 'node:crypto';
import worker from '../server/cpc-integration-staging.mjs';

if (!globalThis.crypto) globalThis.crypto = webcrypto;
const secret = 'synthetic-authorization-token-longer-than-32-chars';
const hits = [];
const env = {
  CPC_API_TOKEN: secret,
  CPC_ENVIRONMENT: 'staging',
  CPC_ALLOWED_HOST: 'preview.example.invalid',
  CPC_DB: {
    prepare(sql) {
      hits.push({sql});
      return {
        bind(...params) {
          hits[hits.length-1].params = params;
          return { async all() { return {results:[{id:'synthetic-link',review_status:'candidate'}]}; }};
        }
      };
    }
  }
};
const url = 'https://preview.example.invalid/internal/evidence-links?entity_ref=IMG:photo_original:test';
async function call(target=url, token=null, method='GET', bindings=env) {
  const headers = token ? {Authorization:'Bearer '+token} : {};
  const response = await worker.fetch(new Request(target,{method,headers}),bindings);
  return {status:response.status,body:await response.json(),headers:response.headers};
}
let r = await call(url);
assert.equal(r.status,401);
assert.equal(hits.length,0);
r = await call(url,'wrong-token-longer-than-32-chars-1234567');
assert.equal(r.status,401);
assert.equal(hits.length,0);
r = await call(url,secret,'POST');
assert.equal(r.status,405);
r = await call(url,secret,'GET',{CPC_API_TOKEN:secret,CPC_ENVIRONMENT:'staging',CPC_ALLOWED_HOST:'preview.example.invalid'});
assert.equal(r.status,503);
r = await call(url,secret,'GET',{...env,CPC_ENVIRONMENT:'production'});
assert.equal(r.status,503);
r = await call(url,secret,'GET',{...env,CPC_ALLOWED_HOST:'production.example.invalid'});
assert.equal(r.status,503);
assert.equal(hits.length,0);
r = await call('https://preview.example.invalid/internal/evidence-links?entity_ref=IMG:photo_original:test%27%20OR%201%3D1',secret);
assert.equal(r.status,400);
assert.equal(hits.length,0);
const withOrigin = await worker.fetch(new Request(url,{headers:{Authorization:'Bearer '+secret,Origin:'https://evil.example'}}),env);
assert.equal(withOrigin.status,403);
assert.equal(hits.length,0);
r = await call(url,secret);
assert.equal(r.status,200);
assert.equal(r.body.links[0].review_status,'candidate');
assert.equal(r.body.review_required,true);
assert.deepEqual(hits[0].params,['IMG:photo_original:test','IMG:photo_original:test']);
assert.ok(hits[0].sql.includes('LIMIT 100'));
assert.ok(!hits[0].sql.includes('synthetic-link'));
assert.equal(r.headers.get('cache-control'),'no-store');
r = await call('https://preview.example.invalid/internal/warren-ocr-review?page=9',secret);
assert.equal(r.status,200);
assert.equal(r.body.page,9);
assert.equal(r.body.review_required,true);
assert.equal(r.body.scan_review_complete,false);
assert.equal(r.body.next_after,null);
assert.deepEqual(hits.at(-1).params,['ma-warren-1849-rice1910',9,'requires_page_image_check','']);
r = await call('https://preview.example.invalid/internal/warren-ocr-review?page=11&after=MA-WARREN-RICE1910-BIRTH-P011-025',secret);
assert.equal(r.status,200);
assert.deepEqual(hits.at(-1).params,['ma-warren-1849-rice1910',11,'requires_page_image_check','MA-WARREN-RICE1910-BIRTH-P011-025']);

assert.ok(hits.at(-1).sql.includes('LIMIT 25'));
assert.ok(!hits.at(-1).sql.includes('raw_record_json'));
const hitCount=hits.length;
r = await call('https://preview.example.invalid/internal/warren-ocr-review?page=11&after=MA-WARREN-RICE1910-BIRTH-P009-025',secret);
assert.equal(r.status,400);
r = await call('https://preview.example.invalid/internal/warren-ocr-review?page=999',secret);
assert.equal(r.status,400);
r = await call('https://preview.example.invalid/internal/warren-ocr-review?page=9&status=reviewed%27%20OR%201=1',secret);
assert.equal(r.status,400);
assert.equal(hits.length,hitCount);
r = await call('https://preview.example.invalid/internal/warren-ocr-review?page=12',secret);
assert.equal(r.status,200);
assert.deepEqual(hits.at(-1).params,['ma-warren-1849-rice1910',12,'requires_page_image_check','']);
r = await call('https://preview.example.invalid/internal/warren-ocr-review?page=10');
assert.equal(r.status,401);
assert.equal(hits.length,hitCount);
r = await call('https://preview.example.invalid/health');
assert.equal(r.status,200);
assert.ok(!JSON.stringify(r.body).includes(secret));
console.log('Staging API authorization, read-only queries and injection controls passed');
