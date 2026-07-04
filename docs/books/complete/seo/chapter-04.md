# Chapter 4: Rendering

**Version:** 1.0

---

# Table of Contents

1. Introduction
2. What is Rendering?
3. HTML Rendering
4. CSS Rendering
5. JavaScript Rendering
6. Client-Side Rendering (CSR)
7. Server-Side Rendering (SSR)
8. Static Site Generation (SSG)
9. Dynamic Rendering
10. Hydration
11. Google Rendering Process
12. Render Queue
13. Render Blocking Resources
14. Lazy Loading
15. JavaScript SEO
16. Images and Rendering
17. CSS Optimization
18. Rendering Issues
19. Rendering Diagnostics
20. SEO Best Practices
21. Checklist
22. Summary
23. References

---

# 1. Introduction

Rendering is the process of converting HTML, CSS, and JavaScript into the final page that users and search engines can see.

Modern websites often depend heavily on JavaScript, making rendering a critical part of technical SEO. If important content is not rendered correctly, search engines may not index it properly.

---

# 2. What is Rendering?

Rendering happens in stages: a browser (or crawler) parses HTML into a DOM tree, applies CSS to build a render tree, executes JavaScript that may modify either, and finally paints the result to the screen. Content and links that only exist after JavaScript executes are invisible to any crawler that stops at the initial HTML.

Rendering enables search engines to:

- Display page content
- Execute JavaScript
- Discover hidden links
- Process dynamic content
- Read structured data
- Understand page layout

Poor rendering can prevent valuable content from appearing in search results at all.

---

# 3. HTML Rendering

The HTML document is parsed into the DOM (Document Object Model), a tree structure representing every element on the page. This is the baseline every crawler can read without executing any JavaScript — content present directly in the initial HTML response is the most universally reliable to have indexed.

---

# 4. CSS Rendering

CSS is parsed into the CSSOM and combined with the DOM to produce the render tree, which determines layout and visual presentation. CSS itself carries no SEO risk directly, but `display: none` or off-screen positioning used to hide content can cause that content to be discounted or treated as cloaking if it doesn't match what's shown to users.

---

# 5. JavaScript Rendering

JavaScript can modify the DOM after initial load — injecting content, links, or entire page sections that didn't exist in the original HTML response. Search engines that don't execute JavaScript (or execute it unreliably) will miss anything added this way. See [Section 15](chapter-04.md) for JavaScript SEO implications specifically.

---

# 6. Client-Side Rendering (CSR)

In CSR, the initial HTML is minimal (often just a single empty `<div id="root">`), and JavaScript builds the entire visible page in the browser after load. This is the highest-risk rendering pattern for SEO — a crawler that doesn't execute JavaScript sees essentially nothing.

---

# 7. Server-Side Rendering (SSR)

In SSR, the server executes the JavaScript framework and returns fully-rendered HTML on the initial request, with JavaScript then "hydrating" the page for interactivity. SSR gives crawlers complete content immediately, without depending on their own JavaScript execution capability.

---

# 8. Static Site Generation (SSG)

SSG pre-renders pages to static HTML at build time, rather than per-request. This provides the same crawler-friendly complete-HTML benefit as SSR with better performance (no per-request server rendering cost), at the tradeoff of needing a rebuild to reflect content changes.

---

# 9. Dynamic Rendering

Dynamic rendering serves a pre-rendered, static version of a page specifically to known crawlers while serving the normal CSR experience to regular users. Google has described this as an acceptable workaround, not cloaking, provided the rendered content is substantively equivalent — but it's a workaround, not a long-term solution; SSR/SSG are the more robust fix.

---

# 10. Hydration

Hydration is the process by which client-side JavaScript "attaches" interactivity to server-rendered HTML that's already visible on the page. Poorly optimized hydration can itself become a performance bottleneck, contributing to poor Interaction to Next Paint (INP) scores ([Chapter 13](chapter-13.md)).

---

# 11. Google Rendering Process

Googlebot crawls in two effective waves: an initial crawl of raw HTML (used for immediate indexing signals and link discovery), followed by a rendering pass using a headless, evergreen Chromium browser that executes JavaScript to see the final DOM. This second wave is queued separately and can lag the initial crawl by anywhere from seconds to several days on large or lower-priority sites.

---

# 12. Render Queue

Because rendering is more computationally expensive than parsing raw HTML, Google maintains a separate render queue with its own prioritization — meaning a page can be crawled promptly but wait considerably longer to have its JavaScript-dependent content actually processed and reflected in the index.

---

# 13. Render Blocking Resources

Render-blocking resources are scripts and stylesheets that the browser must download and process before it can paint any content, delaying Largest Contentful Paint. `seo-playbook page-speed` flags render-blocking `<script>` tags missing `async`/`defer` and excessive render-blocking stylesheets directly.

---

# 14. Lazy Loading

Lazy loading (`loading="lazy"` on images, or JavaScript-based equivalents) defers loading off-screen content until it's needed, improving initial load performance. Content that a user would need to scroll to reach can safely be lazy-loaded; content required for the initial view should not be, since delaying it can itself hurt LCP. `seo-playbook page-speed` flags pages with several images and no lazy loading in use.

---

# 15. JavaScript SEO

JavaScript SEO is the discipline of ensuring JavaScript-dependent content, links, and metadata are still visible to search engines despite the rendering complexity involved — verifying rendered DOM output (not just source HTML), avoiding client-side-only routing that breaks direct URL access, and ensuring critical metadata (title, canonical, meta description) isn't itself injected only after JavaScript runs.

---

# 16. Images and Rendering

Images that are lazy-loaded incorrectly (with no fallback for crawlers that don't scroll or trigger scroll-based loading) or injected entirely via JavaScript risk not being discovered or indexed by image search. Use the standard `loading="lazy"` attribute and real `<img>` tags with `src`/`srcset`, rather than JavaScript-only image injection, wherever possible.

---

# 17. CSS Optimization

Unused or render-blocking CSS delays paint. Common fixes: inline critical above-the-fold CSS directly in `<head>`, defer non-critical stylesheets, and eliminate unused CSS rules from the shipped bundle. `seo-playbook page-speed` flags an excessive count of render-blocking stylesheets as a warning.

---

# 18. Rendering Issues

- Content injected only after user interaction (clicks, hovers) that a crawler never triggers
- Client-side-only routing returning a blank shell for directly-requested URLs
- Metadata (title, canonical, meta description) set only after JavaScript execution
- Infinite scroll with no crawlable paginated fallback
- Excessive hydration cost delaying interactivity and hurting INP

---

# 19. Rendering Diagnostics

- **Google Search Console URL Inspection** — shows Google's actual rendered HTML and a screenshot of what Googlebot saw
- **Chrome DevTools** — disable JavaScript and reload to see the no-JS baseline; use the Rendering tab to simulate slower devices
- **`seo-playbook audit`** — audits the *rendered* HTML you provide, so feeding it post-render output surfaces what a JS-unaware crawler would miss versus what a fully-rendered crawl would see
- **View-source vs. Inspect Element** — view-source shows the initial HTML only; Inspect Element shows the current, JavaScript-modified DOM

---

# 20. SEO Best Practices

- Prefer SSR or SSG over pure CSR for content that needs to rank
- Ensure critical metadata is present in the initial server response, not injected later
- Verify rendered output directly (Search Console URL Inspection), don't assume
- Keep render-blocking resources to a minimum; defer what isn't needed for the initial view
- Provide crawlable, paginated fallbacks for infinite-scroll content

---

# 21. Checklist

- [ ] Critical content and links present in server-rendered HTML, not injected only client-side
- [ ] Title, meta description, and canonical tag present in the initial HTML response
- [ ] Rendered output verified via Search Console URL Inspection, not assumed
- [ ] Render-blocking scripts/stylesheets minimized — `seo-playbook page-speed`
- [ ] Lazy loading applied to below-the-fold images only, not above-the-fold content
- [ ] Infinite scroll has a crawlable, paginated fallback

---

# Summary

Rendering sits between crawling and indexing: a page can be successfully crawled and still fail to be properly indexed if its content only exists after JavaScript execution that a crawler doesn't perform (or delays significantly). Server-side rendering or static generation for anything that needs to rank reliably, verified against actual rendered output rather than assumed, is the most durable fix.

---

# Learning Outcomes

After completing this chapter, you will understand:

- Rendering workflows
- CSR vs SSR vs SSG
- JavaScript SEO
- Render optimization
- Common rendering issues

---

# References

- Google Search Central: JavaScript SEO Basics
- Google Search Central: Understanding the JavaScript SEO Basics — Rendering on Google Search

---

**Next:** Chapter 5 – Indexing
