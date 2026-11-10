// CPC integration staging API — read-only, authenticated, not deployed.
// Required bindings: CPC_DB (D1) and CPC_API_TOKEN (secret).
// No public entity endpoints, no mutation, no automatic source publication.
const ENTITY_REF = /^(?:CEM|VIT|GEO|ICO|CAR|IMG|HIS|KIN|LOC|CON):[a-z][a-z0-9_-]*:[A-Za-z0-9][A-Za-z0-9._-]*$/;

function respond(payload, status = 200) {
  return new Response(JSON.stringify(payload), {
    status, headers: {
      'content-type': 'application/json; charset=utf-8',
      'cache-control': 'no-store',
      'x-content-type-options': 'nosniff',
      'referrer-policy': 'no-referrer'
    }
  });
}
async function digest(value) {
  return new Uint8Array(await crypto.subtle.digest('SHA-256', new TextEncoder().encode(value)));
}
async function authorized(req, secret) {
  const header = req.headers.get('authorization') || '';
  if (typeof secret !== 'string' || secret.length < 32 || !header.startsWith('Bearer ')) return false;
  const supplied = header.slice(7);
  if (supplied.length < 32 || supplied.length > 4096) return false;
  const [a,b] = await Promise.all([digest(supplied),digest(secret)]);
  let different = 0;
  for (let i=0; i<a.length; i++) different |= a[i] ^ b[i];
  return different === 0;
}
export default {
  async fetch(request, env) {
    try {
      const url = new URL(request.url);
      if (request.method !== 'GET') return respond({error:'method_not_allowed'}, 405);
      if (url.pathname === '/health') return respond({service:'cpc-integration-staging',status:'alive'});
      // Never serve internal evidence on an unintended Worker or production host.
      if (env.CPC_ENVIRONMENT !== 'staging' ||
          typeof env.CPC_ALLOWED_HOST !== 'string' ||
          url.hostname !== env.CPC_ALLOWED_HOST)
        return respond({error:'environment_not_authorized'}, 503);
      // Browser-origin requests are not supported by this internal review endpoint.
      // This is defense in depth, not a replacement for authentication.
      if (request.headers.has('origin')) return respond({error:'browser_origin_denied'}, 403);
      if (!await authorized(request, env.CPC_API_TOKEN)) return respond({error:'unauthorized'}, 401);
      if (!env.CPC_DB || typeof env.CPC_DB.prepare !== 'function')
        return respond({error:'db_not_configured'},503);
      if (url.pathname !== '/internal/evidence-links')
        return respond({error:'not_found'},404);
      const ref = url.searchParams.get('entity_ref');
      if (typeof ref !== 'string' || ref.length > 240 || !ENTITY_REF.test(ref))
        return respond({error:'invalid_entity_ref'},400);
      const sql = "SELECT id,source_entity_ref,target_entity_ref,relation,evidence_ref,"
        + " evidence_locator,evidence_note,confidence,review_status,access_scope,"
        + " publication_permission,created_at,reviewed_at,reviewer"
        + " FROM domain_evidence_links WHERE source_entity_ref=? OR target_entity_ref=?"
        + " ORDER BY created_at DESC,id LIMIT 100";
      const result = await env.CPC_DB.prepare(sql).bind(ref,ref).all();
      return respond({entity_ref:ref,review_required:true,links:result.results||[]});
    } catch (error) {
      // No SQL statements, secrets or exact record details in response.
      return respond({error:'internal_error'},500);
    }
  }
};
