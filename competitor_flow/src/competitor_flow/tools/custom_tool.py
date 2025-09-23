from __future__ import annotations
import json
import time
from typing import Optional, List, Dict, Any, Literal, Tuple
from typing_extensions import Annotated
from urllib.parse import urlparse, urlunparse, parse_qsl, urlencode

from pydantic import BaseModel, Field, StringConstraints
from crewai.tools import BaseTool
from ddgs import DDGS
import threading
import math


# -------------------- Rate limiter semplice (token bucket) --------------------

class _TokenBucket:
    def __init__(self, rate_per_sec: float, burst: int):
        self.rate = rate_per_sec        # velocità di “ricarica” token (token/secondo)
        self.burst = burst              # capacità massima del secchio (token massimi accumulabili)
        self.tokens = burst             # token disponibili al momento: parte pieno (puoi fare un burst)
        self.timestamp = time.monotonic()  # ultimo istante in cui abbiamo aggiornato i token
        self.lock = threading.Lock()    # lock per accesso thread-safe (più thread possono consumare)

    def consume(self, tokens: int = 1) -> bool:
        # prova a consumare 'tokens' (di default 1); True se riesce, False se rate-limited
        with self.lock:  # se più thread chiamano consume, evitiamo corse critiche
            now = time.monotonic()                  # tempo corrente ad alta precisione
            elapsed = now - self.timestamp          # secondi passati dall’ultimo aggiornamento
            self.timestamp = now                    # aggiorniamo il riferimento temporale
            # ricarichiamo i token in base al tempo passato, plafonando a 'burst'
            self.tokens = min(self.burst, self.tokens + elapsed * self.rate)
            if self.tokens >= tokens:               # se abbiamo abbastanza token...
                self.tokens -= tokens               # consumiamo
                return True                         # consentiamo l’operazione
            return False                            # altrimenti, rate limit attivo

# Esempio d’uso: 2 ricerche/secondo, burst iniziale di 4
_DDG_BUCKET = _TokenBucket(rate_per_sec=2.0, burst=4)


# ---------------------------- Schema degli argomenti --------------------------
# Quella parte definisce tipi letterali (con Literal) per alcuni parametri del tool. 
# Serve per vincolare i valori accettati e avere validazione automatica da Pydantic.
Region = Literal["wt-wt", "it-it", "us-en", "uk-en", "de-de", "fr-fr", "es-es"]
SafeSearch = Literal["off", "moderate", "strict"]
TimeLimit = Optional[Literal["d", "w", "m", "y"]]

class DuckArgs(BaseModel):
    query: Annotated[
        str,
        StringConstraints(strip_whitespace=True, min_length=2, max_length=300)
    ] = Field(..., description="Search query")
    max_results: Annotated[int, Field(ge=1, le=20)] = Field(
        5, description="Number of results to return (1–20)"
    )
    region: Region = Field("wt-wt", description="Geographic region")
    safesearch: SafeSearch = Field("moderate", description="Content filter")
    timelimit: TimeLimit = Field(None, description="d=day, w=week, m=month, y=year")
    https_only: bool = Field(True, description="Keep only HTTPS results")
    # Facoltativi: aiutano a filtrare o priorizzare domini
    provider: Optional[Literal["azure", "databricks", "neo4j"]] = None
    allow_domains: Optional[List[str]] = Field(
        None,
        description="Explicit allowlist; if set, results not ending with one of these domains are dropped"
    )


# ----------------------------- Tool con guardrail -----------------------------
class DuckDuckGoSearchTool(BaseTool):
    name: str = "duckduckgo_search"
    description: str = (
        "Safe web search via DuckDuckGo. Returns a JSON string list of results: "
        '[{"title":"...","href":"...","body":"..."}]. Enforces input validation, '
        "rate limiting, retries, HTTPS-only (configurable), URL normalization, "
        "and optional domain allowlisting for providers."
    )
    args_schema: type = DuckArgs

    # blocklist minima (puoi estenderla)
    _BLOCKLIST_DOMAINS = {
        "pinterest.com", "reddit.com", "quora.com", "slideshare.net",
        "issuu.com", "scribd.com"
    }

    # allowlist suggerita per provider (puoi estenderla)
    _PROVIDER_ALLOW = {
        "azure": ["microsoft.com", "learn.microsoft.com", "azure.microsoft.com"],
        "databricks": ["databricks.com", "docs.databricks.com"],
        "neo4j": ["neo4j.com", "neo4j.com"],
    }

    def _run(self, **kwargs) -> str:
        # 1) Validazione input (pydantic)
        try:
            args = DuckArgs(**kwargs)
        except Exception as e:
            return json.dumps({"error": f"invalid_args: {str(e)}"}, ensure_ascii=False)

        # 2) Rate limit
        if not _DDG_BUCKET.consume():
            return json.dumps({"error": "rate_limited"}, ensure_ascii=False)

        # 3) Retry con backoff
        attempts = 3
        last_err = None
        for i in range(attempts):
            try:
                results = self._search_once(args)
                # 4) Se tutto ok, ritorna
                return json.dumps(results, ensure_ascii=False)
            except Exception as e:
                last_err = str(e)
                # backoff: 0.5s, 1.0s
                if i < attempts - 1:
                    time.sleep(0.5 * (2 ** i))
        return json.dumps({"error": f"search_failed: {last_err}"}, ensure_ascii=False)

    # -------------------------- Implementazione core --------------------------
    def _search_once(self, args: DuckArgs) -> List[Dict[str, Any]]:
        # Query hard-cap length (già controllata da pydantic); sanitize basilare
        query = " ".join(args.query.split())

        # Esegue la ricerca con timeout DDGS (interno)
        with DDGS() as client:
            if hasattr(client, "text"):
                raw = list(client.text(
                    query=query,
                    region=args.region,
                    safesearch=args.safesearch,
                    timelimit=args.timelimit,
                    max_results=args.max_results
                ))
            else:
                raw = list(client.search(
                    query=query,
                    region=args.region,
                    safesearch=args.safesearch,
                    timelimit=args.timelimit,
                    max_results=args.max_results
                ))

        # Normalizza, filtra, deduplica
        cleaned = []
        seen: set[Tuple[str, str]] = set()  # (host, path)

        # Allowlist derivata dal provider se non passata esplicitamente
        allowlist = set(args.allow_domains or [])
        if args.provider and not args.allow_domains:
            allowlist.update(self._PROVIDER_ALLOW.get(args.provider, []))

        for r in raw:
            url = r.get("href") or r.get("url")
            title = (r.get("title") or "").strip()
            body = (r.get("body") or r.get("snippet") or "").strip()

            if not url or not title:
                continue

            url = self._normalize_url(url, https_only=args.https_only)
            if not url:
                continue

            host = urlparse(url).netloc.lower()

            # blocklist
            if any(host.endswith(b) for b in self._BLOCKLIST_DOMAINS):
                continue

            # allowlist (se presente)
            if allowlist and not any(host.endswith(ad) for ad in allowlist):
                # se non matcha allowlist, scartiamo
                continue

            key = (host, urlparse(url).path or "/")
            if key in seen:
                continue
            seen.add(key)

            # truncate snippet
            if len(body) > 600:
                body = body[:600] + "…"

            cleaned.append({
                "title": title,
                "href": url,
                "body": body
            })

            # fermati appena raggiungi max_results “post-filtri”
            if len(cleaned) >= args.max_results:
                break

        if not cleaned:
            return [{"warning": "no_results_after_filters"}]
        return cleaned

    @staticmethod
    def _normalize_url(url: str, https_only: bool = True) -> Optional[str]:
        try:
            p = urlparse(url)
            scheme = p.scheme.lower() or "https"
            if https_only and scheme != "https":
                return None

            # rimuovi tracking query params
            q_pairs = [(k, v) for (k, v) in parse_qsl(p.query, keep_blank_values=False)
                       if not (k.lower().startswith("utm_") or k.lower() in {"fbclid", "gclid", "igshid"})]
            query = urlencode(q_pairs)

            # normalizza senza fragment
            normalized = urlunparse((scheme, p.netloc.lower(), p.path or "", "", query, ""))
            return normalized
        except Exception:
            return None