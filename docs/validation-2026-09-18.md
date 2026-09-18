# Validation — 18 September 2026

Tested against local Apache 2.4.67 applying the production `.htaccess`, with Lighthouse 13.5.0 and isolated headless Chrome profiles. Mobile uses the default simulated mobile profile; desktop uses Lighthouse's actual desktop configuration. These are local laboratory measurements, not production PageSpeed Insights or field Core Web Vitals.

| Page | Profile | Performance | Accessibility | Best practices | SEO | LCP | CLS | TBT |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Services overview | mobile | 100 | 100 | 100 | 100 | 0.90s | 0.000 | 6ms |
| Services overview | desktop | 100 | 100 | 100 | 100 | 0.24s | 0.000 | 0ms |
| Epoxy flooring | mobile | 100 | 100 | 100 | 100 | 1.65s | 0.000 | 12ms |
| Epoxy flooring | desktop | 100 | 100 | 100 | 100 | 0.42s | 0.000 | 0ms |
| Home construction | mobile | 100 | 100 | 100 | 100 | 1.50s | 0.000 | 8ms |
| Home construction | desktop | 100 | 100 | 100 | 100 | 0.42s | 0.000 | 0ms |
| Siding & finishing | mobile | 100 | 100 | 100 | 100 | 1.35s | 0.000 | 7ms |
| Siding & finishing | desktop | 100 | 100 | 100 | 100 | 0.32s | 0.000 | 0ms |

## Layout and functionality

- 48 Chrome viewport checks across four pages at 320, 390, 680, 681, 768, 980, 981, 1100, 1101, 1440, 1920, and 3840px: no document horizontal overflow, no broken loaded images, and no collapsed epoxy cards. These are viewport checks, not physical TV/iOS/Android device certifications.
- Visual review of the mobile and desktop hero; mobile finish cards use the full available column. AVIF sources load in Chrome; markup retains WebP fallback images.
- FAQ switching closes the prior item, including after keyboard Enter. Shared JavaScript includes a fallback for older browsers without native `details[name]` grouping.
- Anchor navigation reveals the target section. The hero is never marked for fade-in; below-the-fold sections become visible during scrolling.
- Siding form accepts synthetic local QA values and displays “This is a preview. Your request has not been sent.” No lead is sent.
- GTM is the first script in source and its injected loader is async with high fetch priority. This verifies the loader, not production Analytics events or Ads conversions.
- All four pages and robots/sitemap/LLM resources return 200; all checked responses, including 403/404, carry exactly one CSP header. Inline GTM/JSON-LD hashes match; no unsafe-inline or unsafe-eval permissions are added.
- Apache gzip is verified for CSS and XML; image responses have correct AVIF MIME type and the intended cache policy.
- `python3 scripts/validate-site.py`: passes for four pages and 313 local asset/URL references, canonical/sitemap coverage, asset versions, footer links and visible FAQ/schema consistency.
- JavaScript syntax and `git diff --check` pass.

## Remaining production considerations

A score of 100 does not mean every informational Lighthouse opportunity is absent. GTM still includes approximately 76 KiB of unused code in the inspected empty container, which is retained to honor early GTM loading. Lighthouse identifies approximately 39 KiB of potential additional savings for the detailed quartz texture on mobile; AVIF and responsive sizing substantially reduce its transfer size while preserving detail. Small first-party stylesheets remain render-blocking to deliver the correct initial layout.

Measure the public URLs after the user's cPanel deployment. Hosting latency, additional server/proxy CSP headers, compression modules, cache settings and newly published GTM tags can change the results. Webhook delivery remains pending its exact endpoint and CORS setup; the form remains a demonstration. The discovery and structured data files do not guarantee Google ranking or AI recommendations.
