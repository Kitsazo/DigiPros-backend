from .schemas import ServiceOut


SERVICES: list[ServiceOut] = [
    ServiceOut(
        slug="full-service",
        name="Full-service marketing partner",
        tagline="One team. Every channel. Every deliverable.",
        description=(
            "DigiPros is your end-to-end marketing partner. Strategy, "
            "paid media, SEO, content, web, email, analytics, and social "
            "— all under one roof, scoped to your business and your "
            "goals. One contract, one team, one set of dashboards."
        ),
        starts_at="Custom — tailored per engagement",
        deliverables=[
            "Brand strategy & identity systems",
            "Paid advertising across Meta, Google, and TikTok",
            "Search engine optimization & technical SEO",
            "Content marketing, video, and editorial",
            "Web design & high-converting landing pages",
            "Email & CRM lifecycle automation",
            "Analytics, attribution, and dashboards",
            "Always-on social media management",
        ],
        icon="bundle",
    ),
    ServiceOut(
        slug="brand-strategy",
        name="Brand Strategy & Identity",
        tagline="Sharpen positioning, voice, and visual identity.",
        description=(
            "Workshops, market research, and identity systems that give your "
            "brand a confident, recognizable voice across every touchpoint."
        ),
        starts_at="from $3,500",
        deliverables=[
            "Brand audit & competitive analysis",
            "Positioning + messaging framework",
            "Logo, color, and type system",
            "Brand guidelines document",
        ],
        icon="strategy",
    ),
    ServiceOut(
        slug="paid-advertising",
        name="Paid Advertising",
        tagline="Performance ads across Meta, Google, and TikTok.",
        description=(
            "Full-funnel campaign management with creative testing, audience "
            "research, and weekly optimization to maximize ROAS."
        ),
        starts_at="from $1,500 / mo",
        deliverables=[
            "Channel strategy & account setup",
            "Creative production & testing",
            "Weekly optimization sprints",
            "Live performance dashboards",
        ],
        icon="ads",
    ),
    ServiceOut(
        slug="seo",
        name="Search Engine Optimization",
        tagline="Rank for the queries that grow your pipeline.",
        description=(
            "Technical SEO audits, content roadmaps, and link building to "
            "compound organic traffic month over month."
        ),
        starts_at="from $1,200 / mo",
        deliverables=[
            "Technical audit & fixes",
            "Keyword + content strategy",
            "On-page optimization",
            "Authority + link building",
        ],
        icon="seo",
    ),
    ServiceOut(
        slug="content-marketing",
        name="Content Marketing",
        tagline="Editorial, video, and social that actually converts.",
        description=(
            "Editorial calendars, long-form content, and short-form video "
            "production built around what your audience is searching for."
        ),
        starts_at="from $2,000 / mo",
        deliverables=[
            "Editorial calendar",
            "Long-form articles & guides",
            "Short-form video production",
            "Distribution & repurposing",
        ],
        icon="content",
    ),
    ServiceOut(
        slug="web-design",
        name="Web Design & Development",
        tagline="Marketing sites and landing pages that close.",
        description=(
            "High-converting marketing sites, landing pages, and lightweight "
            "web apps designed and built to support your growth motion."
        ),
        starts_at="from $5,000",
        deliverables=[
            "UX research & wireframes",
            "High-fidelity visual design",
            "Build on Webflow / React / Next",
            "A/B testing harness",
        ],
        icon="web",
    ),
    ServiceOut(
        slug="email-crm",
        name="Email & CRM Automation",
        tagline="Nurture sequences and lifecycle marketing.",
        description=(
            "Implement and run lifecycle email programs that convert leads "
            "and re-activate customers — without spamming your list."
        ),
        starts_at="from $1,000 / mo",
        deliverables=[
            "Lifecycle journey mapping",
            "Template & flow build-out",
            "Segmentation & deliverability",
            "Monthly performance review",
        ],
        icon="email",
    ),
    ServiceOut(
        slug="analytics",
        name="Analytics & Attribution",
        tagline="See what's actually working — across channels.",
        description=(
            "GA4, server-side tagging, dashboards, and attribution modeling "
            "so you can make confident decisions with clean data."
        ),
        starts_at="from $2,500",
        deliverables=[
            "Tagging & event plan",
            "GA4 + server-side setup",
            "Dashboard build-out",
            "Quarterly attribution review",
        ],
        icon="analytics",
    ),
    ServiceOut(
        slug="social-media",
        name="Social Media Management",
        tagline="Always-on social presence with bite.",
        description=(
            "Strategy, content production, community management, and "
            "reporting for the platforms that matter to your audience."
        ),
        starts_at="from $1,800 / mo",
        deliverables=[
            "Content pillars & calendar",
            "Daily publishing & engagement",
            "Community management",
            "Monthly insights report",
        ],
        icon="social",
    ),
]


def get_service(slug: str) -> ServiceOut | None:
    return next((s for s in SERVICES if s.slug == slug), None)
