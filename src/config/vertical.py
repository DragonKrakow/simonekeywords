"""
Default seed profile for the client. This is what the agents use as a
starting point before doing their own research — edit this to fit a new
client, or override it per-request from the dashboard / API body.
"""

DEFAULT_CLIENT_PROFILE = {
    "brand": "Simone Guarracino - Luxury Design",
    "business_description": (
        "E-commerce store selling luxury and Art Deco / Gatsby-style "
        "home decor and furniture: velvet armchairs and stools, mirrored "
        "console tables, gold-metal side tables, decorative animal "
        "statues, crystal table lamps, wall clocks, and themed room "
        "collections (Art Deco, Shabby Chic, Nordic, Japandi)."
    ),
    "categories": [
        "Art Deco furniture",
        "velvet armchairs and stools",
        "mirrored console tables",
        "decorative statues and figurines",
        "crystal table lamps",
        "gold metal side tables",
        "glam living room decor",
        "luxury bedroom furniture",
    ],
    "markets": [
        {"country": "United Kingdom", "language": "en", "domain": "simoneguarracino.co.uk"},
        {"country": "Germany", "language": "de", "domain": "simoneguarracino.de"},
        {"country": "Italy", "language": "it", "domain": "simoneguarracino.it"},
        {"country": "Spain", "language": "es", "domain": "simoneguarracino.es"},
        {"country": "France", "language": "fr", "domain": "simoneguarracino.fr"},
    ],
    "platforms": [
        "Google (SEO)",
        "Google Shopping / Ads",
        "Pinterest",
        "Instagram",
        "TikTok",
        "Etsy",
    ],
}
