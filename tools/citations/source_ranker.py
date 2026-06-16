from urllib.parse import urlparse


def rank_sources(sources: list[dict]) -> list[dict]:
    seen_domains: set[str] = set()
    ranked = []
    for item in sources:
        domain = urlparse(item.get("url", "")).netloc
        diversity = 1.0 if domain and domain not in seen_domains else 0.35
        seen_domains.add(domain)
        item["source_diversity_score"] = diversity
        item["final_score"] = round(
            0.45 * float(item.get("relevance_score", 0))
            + 0.25 * float(item.get("credibility_score", 0))
            + 0.20 * float(item.get("freshness_score", 0))
            + 0.10 * diversity,
            3,
        )
        ranked.append(item)
    return sorted(ranked, key=lambda x: x.get("final_score", 0), reverse=True)
