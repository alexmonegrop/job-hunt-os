#!/usr/bin/env python3
"""search-jobs.py - search multiple job boards via python-jobspy and score results.

Pulls scoring keywords from your config:
  - config/user-profile.yaml: target_roles[], target_regions[], target_cities[]
  - config/industries.yaml: industries[].keywords[]
  - config/regions.yaml: regions[].countries[], primary_cities[]

Outputs JSON or a table summary to stdout. Filtered + scored postings can
then be batch-inserted into the database (see the job-search skill).

Usage:
    python tools/job-search/search-jobs.py --query "Program Manager" --location "London"
    python tools/job-search/search-jobs.py --query "AI Product" --location "Berlin" --boards indeed,linkedin --format json

Notes:
    - Glassdoor isn't available everywhere; use indeed,linkedin where it's not.
    - country_indeed must be the full country name (e.g., "united kingdom",
      "germany", "united arab emirates").
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

try:
    from jobspy import scrape_jobs
except ImportError:
    sys.exit("ERROR: python-jobspy not installed. Run: pip install python-jobspy")

try:
    import yaml
except ImportError:
    sys.exit("ERROR: pyyaml not installed. Run: pip install pyyaml")


SCRIPT_DIR = Path(__file__).resolve().parent
REPO_ROOT = SCRIPT_DIR.parent.parent


# --- Default city -> country lookup ---
# Used as a fallback when a city isn't found in the user's regions.yaml.
# Add more here, or override entirely via config/regions.yaml.
DEFAULT_CITY_COUNTRY_MAP = {
    "london": "united kingdom",
    "manchester": "united kingdom",
    "berlin": "germany",
    "munich": "germany",
    "amsterdam": "netherlands",
    "paris": "france",
    "madrid": "spain",
    "barcelona": "spain",
    "milan": "italy",
    "rome": "italy",
    "stockholm": "sweden",
    "copenhagen": "denmark",
    "dublin": "ireland",
    "warsaw": "poland",
    "zurich": "switzerland",
    "new york": "united states",
    "san francisco": "united states",
    "los angeles": "united states",
    "boston": "united states",
    "seattle": "united states",
    "chicago": "united states",
    "austin": "united states",
    "toronto": "canada",
    "vancouver": "canada",
    "montreal": "canada",
    "calgary": "canada",
    "sydney": "australia",
    "melbourne": "australia",
    "singapore": "singapore",
    "tokyo": "japan",
    "hong kong": "hong kong",
    "dubai": "united arab emirates",
    "abu dhabi": "united arab emirates",
    "riyadh": "saudi arabia",
    "jeddah": "saudi arabia",
    "doha": "qatar",
    "bahrain": "bahrain",
    "kuwait": "kuwait",
    "muscat": "oman",
    "tel aviv": "israel",
    "mumbai": "india",
    "bangalore": "india",
    "delhi": "india",
}


def load_yaml(path: Path) -> dict:
    if not path.exists():
        return {}
    try:
        with open(path, encoding="utf-8") as f:
            return yaml.safe_load(f) or {}
    except yaml.YAMLError as e:
        print(f"WARNING: Could not parse {path}: {e}", file=sys.stderr)
        return {}


def load_user_profile() -> dict:
    return load_yaml(REPO_ROOT / "config" / "user-profile.yaml")


def load_industries() -> dict:
    return load_yaml(REPO_ROOT / "config" / "industries.yaml")


def load_regions() -> dict:
    return load_yaml(REPO_ROOT / "config" / "regions.yaml")


def build_city_country_map(regions_cfg: dict) -> dict[str, str]:
    """Build a city-to-country lookup from regions.yaml + the default map."""
    city_to_country: dict[str, str] = dict(DEFAULT_CITY_COUNTRY_MAP)
    for region in regions_cfg.get("regions", []) or []:
        countries = region.get("countries", []) or []
        primary_cities = region.get("primary_cities", []) or []
        if not countries:
            continue
        country = countries[0].lower()
        for city in primary_cities:
            city_to_country[city.lower()] = country
    return city_to_country


def auto_detect_country(location: str, city_country_map: dict[str, str]) -> str | None:
    """Detect Indeed country string from a free-form location."""
    loc_lower = location.lower().strip()
    for city, country in city_country_map.items():
        if city in loc_lower:
            return country
    return None


def build_relevant_title_keywords(profile: dict) -> list[str]:
    """Build the title-screening keyword list from target_roles[]."""
    roles = profile.get("target_roles", []) or []
    keywords: list[str] = []
    for role in roles:
        keywords.append(role.lower())
        # Also include the head-noun (last 1-2 words) for partial matches.
        words = role.lower().split()
        if len(words) >= 2:
            keywords.append(" ".join(words[-2:]))
    # De-duplicate while preserving order.
    seen: set[str] = set()
    out = []
    for kw in keywords:
        if kw not in seen:
            seen.add(kw)
            out.append(kw)
    return out


def build_role_keywords(profile: dict) -> dict[str, int]:
    """Score map for role keywords pulled from target_roles[]."""
    roles = profile.get("target_roles", []) or []
    out: dict[str, int] = {}
    for role in roles:
        out[role.lower()] = 3       # exact match: top tier
        words = role.lower().split()
        if len(words) >= 2:
            out[" ".join(words[-2:])] = 2
    # Generic seniority/role qualifiers (always relevant).
    for kw in ("director", "head of", "lead", "senior", "vp"):
        out.setdefault(kw, 1)
    return out


def build_region_keywords(profile: dict, regions_cfg: dict) -> dict[str, int]:
    """Score map for region/geography keywords."""
    out: dict[str, int] = {}
    for region in profile.get("target_regions", []) or []:
        out[region.lower()] = 2
    for city in profile.get("target_cities", []) or []:
        out[city.lower()] = 2
    for region in regions_cfg.get("regions", []) or []:
        for city in region.get("primary_cities", []) or []:
            out.setdefault(city.lower(), 2)
        for country in region.get("countries", []) or []:
            out.setdefault(country.lower(), 2)
    return out


def build_industry_keywords(profile: dict, industries_cfg: dict) -> dict[str, int]:
    """Score map for industry keywords. Uses target_industries[] + the
    keywords[] list from each industry in industries.yaml."""
    target_industries = {i.lower() for i in profile.get("target_industries", []) or []}
    out: dict[str, int] = {}
    for ind in industries_cfg.get("industries", []) or []:
        name = (ind.get("name") or "").lower()
        weight = 2 if name in target_industries else 1
        if name:
            out[name] = max(out.get(name, 0), weight)
        for kw in ind.get("keywords", []) or []:
            kw_lc = kw.lower()
            out[kw_lc] = max(out.get(kw_lc, 0), weight)
    return out


def is_relevant_title(title: str, relevant_title_keywords: list[str]) -> bool:
    title_lower = title.lower()
    return any(kw in title_lower for kw in relevant_title_keywords)


def calculate_fit_score(title: str, description: str, company: str, location: str,
                        role_keywords: dict[str, int], region_keywords: dict[str, int],
                        industry_keywords: dict[str, int]) -> dict:
    text = f"{title} {description} {company} {location}".lower()

    role_score = 0
    for kw, pts in role_keywords.items():
        if kw in text:
            role_score = max(role_score, pts)

    region_score = 0
    for kw, pts in region_keywords.items():
        if kw in text:
            region_score = max(region_score, pts)

    industry_score = 0
    for kw, pts in industry_keywords.items():
        if kw in text:
            industry_score = max(industry_score, pts)

    seniority = 1 if any(kw in text for kw in ("senior", "director", "vp", "head of", "lead")) else 0
    geo = 1 if any(kw in text for kw in ("remote", "hybrid")) or region_score > 0 else 0

    total = min(role_score + region_score + industry_score + seniority + geo, 10)

    return {
        "total": total,
        "role_alignment": role_score,
        "region_signal": region_score,
        "industry_match": industry_score,
        "seniority_fit": seniority,
        "geography_match": geo,
    }


def search_and_score(query: str, location: str, boards: list[str], results_wanted: int,
                     country: str | None,
                     relevant_title_keywords: list[str],
                     role_keywords: dict[str, int],
                     region_keywords: dict[str, int],
                     industry_keywords: dict[str, int]) -> list[dict]:
    kwargs = {
        "site_name": boards,
        "search_term": query,
        "location": location,
        "results_wanted": results_wanted,
    }
    if country:
        kwargs["country_indeed"] = country
    try:
        jobs_df = scrape_jobs(**kwargs)
    except Exception as e:
        print(f"Search error: {e}", file=sys.stderr)
        return []

    results = []
    skipped_titles = 0
    for _, row in jobs_df.iterrows():
        title = str(row.get("title", ""))
        if not is_relevant_title(title, relevant_title_keywords):
            skipped_titles += 1
            continue

        description = str(row.get("description", ""))[:500]
        company = str(row.get("company_name", ""))
        loc = str(row.get("location", ""))
        url = str(row.get("job_url", ""))
        board = str(row.get("site", ""))
        date_posted = str(row.get("date_posted", ""))

        score = calculate_fit_score(title, description, company, loc,
                                    role_keywords, region_keywords, industry_keywords)

        results.append({
            "title": title,
            "company": company,
            "location": loc,
            "job_url": url,
            "board": board,
            "date_posted": date_posted,
            "description_preview": description[:200],
            "fit_score": score,
        })

    if skipped_titles > 0:
        print(f"Filtered out {skipped_titles} irrelevant titles", file=sys.stderr)

    results.sort(key=lambda x: -x["fit_score"]["total"])
    return results


def main() -> int:
    parser = argparse.ArgumentParser(description="Search job boards and score results")
    parser.add_argument("--query", required=True, help="Job search query")
    parser.add_argument("--location", required=True, help="Location to search (city, country)")
    parser.add_argument("--boards", default="indeed,linkedin",
                        help="Comma-separated board names (e.g., indeed,linkedin,glassdoor)")
    parser.add_argument("--results", type=int, default=20, help="Results per board")
    parser.add_argument("--country", default=None,
                        help="Country for Indeed (auto-detected from location if omitted)")
    parser.add_argument("--min-score", type=int, default=0,
                        help="Minimum fit score to include in output")
    parser.add_argument("--format", choices=["json", "table"], default="table",
                        help="Output format")
    args = parser.parse_args()

    profile = load_user_profile()
    industries_cfg = load_industries()
    regions_cfg = load_regions()

    if not profile:
        print(
            "WARNING: config/user-profile.yaml not found. Title and scoring will be lenient.\n"
            "         Copy config/user-profile.example.yaml -> config/user-profile.yaml and customise.",
            file=sys.stderr,
        )

    city_country_map = build_city_country_map(regions_cfg)
    country = args.country or auto_detect_country(args.location, city_country_map)
    if not country:
        print(
            f"WARNING: Could not auto-detect country for location '{args.location}'.\n"
            f"         Pass --country <name> explicitly or add the city to config/regions.yaml.",
            file=sys.stderr,
        )

    relevant_title_keywords = build_relevant_title_keywords(profile) or [
        # Fallback: very lenient default if no profile.
        "manager", "director", "lead", "head", "vp", "founder",
    ]
    role_keywords = build_role_keywords(profile)
    region_keywords = build_region_keywords(profile, regions_cfg)
    industry_keywords = build_industry_keywords(profile, industries_cfg)

    boards = [b.strip() for b in args.boards.split(",")]
    print(f"Searching: '{args.query}' in {args.location} on {', '.join(boards)} (country={country})...",
          file=sys.stderr)

    results = search_and_score(args.query, args.location, boards, args.results, country,
                                relevant_title_keywords, role_keywords,
                                region_keywords, industry_keywords)

    if args.min_score > 0:
        results = [r for r in results if r["fit_score"]["total"] >= args.min_score]

    if args.format == "json":
        print(json.dumps(results, indent=2, default=str))
    else:
        print(f"\nFound {len(results)} results:\n")
        print(f"{'#':>3} | {'Score':>5} | {'Company':<25} | {'Title':<40} | {'Location':<20} | {'Board':<10}")
        print("-" * 115)
        for i, r in enumerate(results, 1):
            score = r["fit_score"]["total"]
            marker = "***" if score >= 6 else "  *" if score >= 4 else "   "
            company = (r["company"] or "?")[:25]
            print(f"{i:>3} | {score:>4}{marker} | {company:<25} | {r['title'][:40]:<40} | {r['location'][:20]:<20} | {r['board']:<10}")
        print("\n*** = Proceed (>=6)  * = Review (4-5)  blank = Skip (<4)")
        print(f"Total qualifying (>=6): {sum(1 for r in results if r['fit_score']['total'] >= 6)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
