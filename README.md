# Space Up Construction — Landing Pages

Static landing pages built with HTML and CSS only.

- `/epoxy-flooring/` — Epoxy flooring for garages and commercial spaces
- `/home-construction/` — New home construction and home remodeling
- `/siding-finishing/` — Siding, painting, drywall, plaster, and finish carpentry

## Local preview

Open `index.html` in a browser or serve the repository with any static HTTP server.

## Google Tag Manager and CSP

`GTM-52FS343L` is installed on the index and all three landing pages. GTM is the first script in the head: preconnect, preload, and a high-priority async request start loading it before the page stylesheet and images. The noscript iframe is the first element in the body and uses `hidden` instead of an inline style.

`.htaccess` is the CSP source of truth. Apache `mod_headers` and `AllowOverride FileInfo` must be enabled. The deployment recipe explicitly copies `.htaccess`; no CSP meta tags compete with the HTTP header. The header is sent on successful responses and errors, with one policy value.

These static pages authorize the exact inline bootstrap with a SHA-256 CSP hash. If the bootstrap changes (including whitespace), recalculate the hash from the text inside the script element and update `script-src` in `.htaccess`. Do not use a fixed nonce or allow `unsafe-inline` / `unsafe-eval`.

| Integration | Allowed resources |
| --- | --- |
| GTM | Google Tag Manager scripts, connections, pixels and frames |
| Analytics | GA4 connections and pixels on the Google Analytics / Analytics endpoints, plus the advertising endpoints documented by Google |
| Google Ads | Google Ads scripts, connections and pixels on the explicit Google Ads, DoubleClick, Google and Google Syndication hosts |
| YouTube | Standard and privacy embed paths; IFrame API scripts; thumbnails on `i.ytimg.com` |
| Webhook | Local same-origin requests only until the exact external HTTPS webhook URL is confirmed |

Permissions are scoped by resource type. YouTube video/CDN requests happen within its iframe; the parent page does not need a broad `googlevideo.com` or `gstatic.com` permission. Google regional endpoints are listed explicitly for `.com` and `.com.br`; add any other required Google country host individually. Custom JavaScript variables and arbitrary inline Custom HTML tags are restricted: use native tags or sandboxed custom templates. Tag Assistant preview requires additional development-only origins from the [Google CSP guide](https://developers.google.com/tag-platform/security/guides/csp).

For a webhook, allow only its confirmed HTTPS URL in `connect-src`. CSP does not grant CORS access: the endpoint must separately accept the site origin and, for JSON POSTs, the OPTIONS preflight. Never embed private webhook credentials in frontend files.

The publicly served GTM container was version 1 with no tags at inspection time. Loader tests do not establish Analytics collection or Ads conversion recording; these require configured tags/IDs. The siding form remains a local demonstration and does not send leads.

Deployment remains manual in cPanel: **Update from Remote → Deploy HEAD Commit**. After deployment verify that all four HTML responses have exactly one `Content-Security-Policy` header, then use Tag Assistant with the actual published tags and inspect CSP/CORS errors. Any additional proxy CSP combines with this policy and must also allow the needed sources.

### Validation before deployment

Validated with local Apache using the actual `.htaccess`: all four HTML pages return HTTP 200 with one CSP header and a matching GTM hash; 403/404 responses retain the header. Browser smoke tests loaded GTM, the GA4 loader (a test ID with no `config` call), Google Ads' async loader, YouTube IFrame API, and both standard/privacy embeds. An unauthorized external script was blocked. CSS, the exclusive FAQ, and the siding demonstration form continued working. No real conversion, Analytics configuration event, lead, or webhook POST was sent. Webhook CSP/CORS and actual event delivery remain untested until the endpoint and active tags are supplied.
