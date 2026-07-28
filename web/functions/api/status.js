// Approve/reject state for the review gallery, stored in D1.
//
// Deliberately tiny: the gallery already falls back to localStorage when this isn't reachable,
// so this only has to do one job — keep the decision when you open the page on another device.

const CORS = { "content-type": "application/json" };
const VALID = new Set(["approved", "rejected", "pending"]);

export async function onRequestGet({ env }) {
  const { results } = await env.DB.prepare(
    "SELECT id, status FROM review ORDER BY id"
  ).all();
  const out = {};
  for (const row of results) out[row.id] = row.status;
  return new Response(JSON.stringify(out), { headers: CORS });
}

export async function onRequestPost({ request, env }) {
  let body;
  try {
    body = await request.json();
  } catch {
    return new Response(JSON.stringify({ error: "bad json" }), { status: 400, headers: CORS });
  }

  const { id, status } = body ?? {};
  // ids come from the manifest, but this endpoint is public — validate rather than trust
  if (typeof id !== "string" || !id || id.length > 200 || !VALID.has(status)) {
    return new Response(JSON.stringify({ error: "bad id or status" }),
      { status: 400, headers: CORS });
  }

  await env.DB.prepare(
    `INSERT INTO review (id, status, updated_at) VALUES (?1, ?2, datetime('now'))
     ON CONFLICT(id) DO UPDATE SET status = ?2, updated_at = datetime('now')`
  ).bind(id, status).run();

  return new Response(JSON.stringify({ ok: true, id, status }), { headers: CORS });
}
