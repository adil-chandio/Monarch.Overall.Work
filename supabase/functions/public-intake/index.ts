import { createClient } from "https://esm.sh/@supabase/supabase-js@2.47.10";

const corsHeaders = {
  "Access-Control-Allow-Origin": "*",
  "Access-Control-Allow-Headers": "authorization, x-client-info, apikey, content-type",
  "Access-Control-Allow-Methods": "POST, OPTIONS",
};

Deno.serve(async (req: Request) => {
  if (req.method === "OPTIONS") {
    return new Response("ok", { headers: corsHeaders });
  }

  if (req.method !== "POST") {
    return new Response(JSON.stringify({ ok: false, error: "Method not allowed" }), {
      status: 405,
      headers: { ...corsHeaders, "Content-Type": "application/json" },
    });
  }

  try {
    const payload = await req.json();
    const clientName = String(payload.name || payload.client_name || "").trim();
    const clientEmail = String(payload.email || payload.client_email || "").trim().toLowerCase();
    const projectBrief = String(payload.message || payload.project_brief || "").trim();

    if (!clientName || !clientEmail || !clientEmail.includes("@") || projectBrief.length < 5) {
      return new Response(
        JSON.stringify({
          ok: false,
          error: "Please provide your name, valid email, and a short project brief (5+ chars).",
        }),
        { status: 400, headers: { ...corsHeaders, "Content-Type": "application/json" } },
      );
    }

    const supabaseUrl = Deno.env.get("SUPABASE_URL")!;
    const serviceRoleKey = Deno.env.get("SUPABASE_SERVICE_ROLE_KEY")!;
    const supabase = createClient(supabaseUrl, serviceRoleKey);

    const { data, error } = await supabase.rpc("submit_client_inquiry", {
      p_client_name: clientName,
      p_client_email: clientEmail,
      p_company_or_brand: String(payload.company || payload.company_or_brand || ""),
      p_whatsapp_or_telegram: String(payload.whatsapp || payload.whatsapp_or_telegram || ""),
      p_service_slug: String(payload.service || payload.service_slug || "signature-websites"),
      p_budget_tier: String(payload.budget || payload.budget_tier || "$280 - $650"),
      p_preferred_rail: String(payload.preferred_rail || "foreign_fiat"),
      p_project_brief: projectBrief,
      p_reference_links: String(payload.reference_links || ""),
      p_source: String(payload.source || "portfolio_v37"),
    });

    if (error) {
      return new Response(JSON.stringify({ ok: false, error: error.message }), {
        status: 400,
        headers: { ...corsHeaders, "Content-Type": "application/json" },
      });
    }

    return new Response(
      JSON.stringify({
        ok: true,
        ...data,
        portal_hub: "https://monarch-workspace-beryl.vercel.app/",
      }),
      { status: 200, headers: { ...corsHeaders, "Content-Type": "application/json" } },
    );
  } catch (err) {
    return new Response(
      JSON.stringify({ ok: false, error: err instanceof Error ? err.message : "Invalid JSON payload" }),
      { status: 400, headers: { ...corsHeaders, "Content-Type": "application/json" } },
    );
  }
});
