# Security Policy

## Reporting a vulnerability

Please report security issues privately through GitHub's [private vulnerability reporting](https://github.com/jumma786/seo-aeo-playbook/security/advisories/new) rather than opening a public issue.

Expect an initial response within a week. This is a small project maintained in spare time, so please set expectations accordingly.

## Scope and trust model

Read this before deploying anything here — some of it is intentional design, not oversight.

**The API has no authentication, deliberately.** `api/` is built for local use alongside the CLI on a machine you control. It is not a multi-tenant service and has no authentication, authorisation, or rate limiting. **Do not expose it to the public internet.** If you need to, put it behind your own authenticating proxy and treat every endpoint as untrusted input.

**Several tools make outbound requests to URLs you supply.** `seo_audit`, `page_speed`, `site_audit`, and `link_checker` fetch arbitrary URLs. If you wrap any of these in a service that accepts URLs from other people, you have built a server-side request forgery vector: a caller can point it at your internal network or cloud metadata endpoints. The library does not defend against this, because as a local CLI it does not need to. That defence is yours to add.

**Two API endpoints deviate from the CLI on purpose.** The location-page and service-page endpoints return rendered content in the response instead of writing files to a server-side path, and the book-docs endpoints take filename/content pairs rather than a directory path. Both avoid arbitrary file write and path traversal from client-supplied input. Please preserve these properties if you extend those routes.

**Generated output is not sanitised for hostile input.** Schema, sitemap, robots.txt, and page generators assume you control their inputs. Feeding them untrusted data and publishing the result is on you.

## Not in scope

- The books, prompts, and checklists are documentation. Factual errors in them are bugs, but not security bugs — please open a normal issue.
- Findings that depend on exposing the unauthenticated API publicly, which this document tells you not to do.
