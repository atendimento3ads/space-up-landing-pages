# Space Up Construction — Landing Pages

Static landing pages built with HTML, mobile-first CSS, and lightweight progressive JavaScript.

- `/epoxy-flooring/` — Epoxy flooring for garages and commercial spaces
- `/home-construction/` — New home construction and home remodeling
- `/siding-finishing/` — Siding, painting, drywall, plaster, and finish carpentry

## Local preview

Serve the repository with a static HTTP server (`python3 -m http.server 8767`). To validate production headers, use Apache with `mod_headers`, `mod_mime`, and `AllowOverride FileInfo`; a simple static server does not apply `.htaccess`.

## Google Tag Manager and CSP

`GTM-52FS343L` is installed on the index and all three landing pages. GTM is the first script in the head: preconnect, preload, and a high-priority async request start loading it before the page stylesheet and images. The noscript iframe is the first element in the body and uses `hidden` instead of an inline style.

`.htaccess` is the CSP source of truth. Apache `mod_headers` and `AllowOverride FileInfo` must be enabled. The deployment recipe explicitly copies `.htaccess`; no CSP meta tags compete with the HTTP header. The header is sent on successful responses and errors, with one policy value.

These static pages authorize the exact inline bootstrap and JSON-LD blocks with SHA-256 CSP hashes. If any inline script changes (including whitespace), run `python3 scripts/update-assets.py` to recalculate the hashes in `script-src`. The same command refreshes content-based query versions for local CSS/JS, avoiding stale styles after a deployment. Do not use a fixed nonce or allow `unsafe-inline` / `unsafe-eval`.

| Integration | Allowed resources |
| --- | --- |
| GTM | Google Tag Manager scripts, connections, pixels and frames |
| Analytics | GA4 connections and pixels on the Google Analytics / Analytics endpoints, plus the advertising endpoints documented by Google |
| Google Ads | Google Ads scripts, connections and pixels on the explicit Google Ads, DoubleClick, Google and Google Syndication hosts |
| YouTube | Standard and privacy embed paths; IFrame API scripts; thumbnails on `i.ytimg.com` |
| Quote forms | Same-origin `POST` to `/submit-quote.php`; no external webhook or plugin |

Permissions are scoped by resource type. YouTube video/CDN requests happen within its iframe; the parent page does not need a broad `googlevideo.com` or `gstatic.com` permission. Google regional endpoints are listed explicitly for `.com` and `.com.br`; add any other required Google country host individually. Custom JavaScript variables and arbitrary inline Custom HTML tags are restricted: use native tags or sandboxed custom templates. Tag Assistant preview requires additional development-only origins from the [Google CSP guide](https://developers.google.com/tag-platform/security/guides/csp).

The Epoxy Flooring and Siding forms post to a same-origin PHP endpoint, so the current `connect-src 'self'` and `form-action 'self'` directives already cover submission. The endpoint validates every field again, rejects cross-origin requests, uses a honeypot and per-IP rate limit, and deduplicates retries with a per-submission identifier. It sends plain-text mail through the cPanel/PHP local mail transport. Messages go to `contact@spaceupconstruction.com`; the validated visitor address is used only as `Reply-To`. No mail credentials or external service are exposed in frontend files.

The publicly served GTM container was version 1 with no tags at inspection time. Loader tests do not establish Analytics collection or Ads conversion recording; these require configured tags/IDs.

Deployment remains manual in cPanel: **Update from Remote → Deploy HEAD Commit**. After deployment verify that all four HTML responses have exactly one `Content-Security-Policy` header, then use Tag Assistant with the actual published tags and inspect CSP/CORS errors. Any additional proxy CSP combines with this policy and must also allow the needed sources.

The Meta HTML verification file `7g70voolv25xx4zh31wo93uk6a16y0.html` is copied to the root of this cPanel deployment. This repository serves `services.spaceupconstruction.com`; Meta's supplied instructions target `spaceupconstruction.com`, which is currently served by Wix. Verifying the apex domain therefore also requires placing the token through Wix or using Meta's DNS verification option for the apex domain.

### Validation before deployment

Validated with local Apache using the actual `.htaccess`: all four HTML pages return HTTP 200 with one CSP header and a matching GTM hash; 403/404 responses retain the header. Browser smoke tests loaded GTM, the GA4 loader (a test ID with no `config` call), Google Ads' async loader, YouTube IFrame API, and both standard/privacy embeds. An unauthorized external script was blocked. CSS and the exclusive FAQ continued working. The browser form flow was tested against controlled same-origin success and failure responses without sending a real lead, and the PHP endpoint passed static syntax parsing. Confirm mailbox delivery once after the cPanel deployment because the local environment cannot inspect the hosting account's mail queue, SPF, DKIM, or mail logs.


## Mobile-first layouts and motion

Always implement the small-screen layout first. Shared styles live in `assets/site.css`, with enhancements at `min-width: 681px` and `981px`. Siding adds its own mobile-first styles. Content is bounded to a readable width on larger displays; fluid typography, flexible columns, wrapped contact links, 44px controls, and the bottom call button cover small screens and safe areas.

`assets/site.js` progressively adds one-time fade/translate effects below the hero using IntersectionObserver, without continuous scroll listeners. Above-the-fold content appears immediately. Content remains visible without JavaScript, with reduced motion, when printing, and when focused. Smooth anchor scrolling respects reduced-motion preferences. FAQs use native grouped details and a JavaScript compatibility fallback, preserving keyboard interaction.

## Performance and image sources

Content images use responsive AVIF sources with WebP fallbacks, explicit dimensions, async decoding, and native lazy loading below the fold. Hero images load eagerly with high priority. System fonts avoid external font downloads and font-related layout shifts. Original assets remain available; responsive variants are generated from those originals with the same aspect ratios.

Apache compresses textual responses when `mod_filter`/`mod_deflate` are available. HTML, XML, and text discovery files revalidate; CSS/JS cache for one hour and images for one week. Stable filenames are deliberately not marked immutable. After changing CSS/JS, refresh their content versions before committing:

```sh
python3 scripts/update-assets.py
python3 scripts/validate-site.py
```

The dependency-free validator checks local URLs, image sources, canonical URLs, sitemap coverage, asset versions, footer credits, FAQ schema against visible answers, and every inline CSP hash. Deployment includes the new shared `assets` directory, favicon, and discovery files.

## Search and AI discovery

Each page has a unique, service-specific title and description, canonical URL, social preview metadata, one H1, natural service/location terms, crawlable text, and links to the other services. JSON-LD describes the contractor, service, website/page, page hierarchy, and the visible FAQs. Contact/address data is consistent across the pages. No ratings, reviews, prices, licenses, or certifications are invented.

`sitemap.xml` lists the four canonical pages. `robots.txt` permits crawling and links to the sitemap. `llm.txt` fulfills the requested filename; `llms.txt` provides the same factual Markdown summary under the proposed convention. These discovery files do not guarantee indexing, ranking, AI recommendations, or rich results. Google recommends foundational SEO for its AI search features; it does not require special AI text files ([official guide](https://developers.google.com/search/docs/fundamentals/ai-optimization-guide)).

Submit the production sitemap in Google Search Console after the manual cPanel deployment. Production PageSpeed results and Core Web Vitals depend on the hosting response time, cache/compression modules, device/network, and the tags actually published in GTM; local laboratory results are not field measurements. After deployment, submit one synthetic form request and confirm it in `contact@spaceupconstruction.com`; if it is delayed, inspect cPanel Email Deliverability and Track Delivery before changing application code.

The current local audit results and functional checks are recorded in [docs/validation-2026-09-18.md](docs/validation-2026-09-18.md), with machine-readable scores in the adjacent JSON summary.
