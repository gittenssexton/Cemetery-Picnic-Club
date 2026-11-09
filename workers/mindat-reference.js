/**
 * Cemetery Picnic Club — optional Mindat reference lookup.
 * Deploy as a Cloudflare Worker after verifying Mindat permissions.
 * Never place API keys or this lookup credential in browser code.
 */
const json = (body, status = 200) => new Response(JSON.stringify(body), {
  status, headers: { "content-type": "application/json; charset=utf-8", "cache-control": "no-store", "x-content-type-options": "nosniff" }
});
export default {
  async fetch(request, env) {
    const url = new URL(request.url);
    if (url.pathname === "/health") {
      return json({ service: "cpc-mindat-reference", configured: Boolean(env.MINDAT_API_TOKEN), enabled: env.MINDAT_LOOKUP_ENABLED === "true" });
    }
    if (url.pathname !== "/api/reference/mindat/search" || request.method !== "GET") {
      return json({ error: "Not found" }, 404);
    }
    // Deliberately disabled pending written authorization for the proposed use.
    if (env.MINDAT_LOOKUP_ENABLED !== "true") return json({ error: "Mindat lookup disabled pending permissions" }, 503);
    if (!env.MINDAT_API_TOKEN || !env.CPC_REFERENCE_ACCESS_TOKEN) return json({ error: "Server not configured" }, 503);
    const provided = request.headers.get("Authorization");
    if (!provided || provided !== `Bearer ${env.CPC_REFERENCE_ACCESS_TOKEN}`) return json({ error: "Unauthorized" }, 401);
    const query = (url.searchParams.get("q") || "").trim();
    if (query.length < 2 || query.length > 80 || !/^[\p{L}\p{N} .,'()\-]+$/u.test(query)) {
      return json({ error: "Invalid mineral search term" }, 400);
    }
    const upstream = new URL("https://api.mindat.org/geomaterials-search/");
    upstream.searchParams.set("q", query);
    upstream.searchParams.set("size", "8");
    try {
      const response = await fetch(upstream, {
        headers: { Authorization: `Token ${env.MINDAT_API_TOKEN}`, Accept: "application/json" },
        signal: AbortSignal.timeout(8000)
      });
      if (!response.ok) return json({ error: "Upstream lookup failed", status: response.status }, 502);
      const data = await response.json();
      const results = Array.isArray(data) ? data.slice(0, 8).map(item => ({
        id: item.id, name: item.name, ima_status: item.ima_status ?? null
      })) : [];
      return json({ source: "Mindat", query, results, usage: "human-reviewed reference only; not AI model grounding" });
    } catch {
      return json({ error: "Upstream unavailable" }, 502);
    }
  }
};
