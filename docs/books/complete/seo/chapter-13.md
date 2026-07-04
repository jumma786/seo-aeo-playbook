# Chapter 13: Core Web Vitals

**Version:** 1.0

---

# Table of Contents

1. Introduction
2. What are Core Web Vitals?
3. Why Core Web Vitals Matter
4. Largest Contentful Paint (LCP)
5. Interaction to Next Paint (INP)
6. Cumulative Layout Shift (CLS)
7. Mobile Performance
8. Desktop Performance
9. Page Speed
10. Render Blocking Resources
11. Image Optimization
12. Font Optimization
13. JavaScript Optimization
14. CSS Optimization
15. Lazy Loading
16. Browser Caching
17. Content Delivery Networks (CDNs)
18. Performance Monitoring
19. Google PageSpeed Insights
20. Lighthouse
21. Chrome DevTools
22. Search Console Reports
23. Common Performance Issues
24. Optimization Checklist
25. Best Practices
26. Summary
27. References

---

# 1. Introduction

Core Web Vitals are a set of user experience metrics introduced by Google to measure loading performance, responsiveness, and visual stability. These metrics help website owners identify performance issues that affect both users and search visibility.

---

# 2. What are Core Web Vitals?

Core Web Vitals are three standardized, field-measurable metrics — LCP, INP, and CLS — that Google uses as a quantified proxy for page experience, part of the broader user-experience ranking signal ([Chapter 6, Section 12](chapter-06.md)). Unlike many SEO signals, Core Web Vitals are measured directly from real user visits (field data via the Chrome User Experience Report), not just estimated in a lab.

---

# 3. Why Core Web Vitals Matter

Core Web Vitals matter for two independent reasons: they're a Google ranking signal (a modest one, among hundreds), and — more significantly in practice — they directly affect conversion, bounce rate, and user satisfaction. A slow, janky, unresponsive page loses users regardless of how it ranks.

---

# 4. Largest Contentful Paint (LCP)

Measures how quickly the main content of a page becomes visible.

Target: **≤ 2.5 seconds**

LCP is most commonly delayed by slow server response time (TTFB), render-blocking resources, slow-loading images/fonts, or client-side rendering delaying the main content entirely. `seo-playbook page-speed` measures genuine time-to-first-byte and flags several of LCP's common root causes directly.

---

# 5. Interaction to Next Paint (INP)

Measures how quickly a page responds to user interactions.

Target: **≤ 200 milliseconds**

INP (which replaced First Input Delay as a Core Web Vital in 2024) measures the full round-trip from user interaction to the next visual update, across all interactions during a page visit — not just the first one. Heavy JavaScript execution, excessive hydration cost ([Chapter 4, Section 10](chapter-04.md)), and large, unoptimized event handlers are common causes of poor INP.

---

# 6. Cumulative Layout Shift (CLS)

Measures visual stability by tracking unexpected layout movement.

Target: **≤ 0.1**

CLS is most commonly caused by images or ads without reserved dimensions, web fonts causing a layout reflow when they load, or content dynamically injected above already-rendered content. Explicit `width`/`height` attributes on every image are the single highest-leverage fix — `seo-playbook page-speed` flags images missing these attributes directly.

---

# 7. Mobile Performance

Mobile devices typically have less processing power and slower network conditions than desktop, making mobile performance the more consequential measurement under mobile-first indexing ([Chapter 15](chapter-15.md)) — Google evaluates the mobile experience, not the desktop one, for ranking purposes.

---

# 8. Desktop Performance

Desktop performance still matters for the substantial share of traffic (and, in some verticals, majority of conversions) that occurs on desktop, even though it isn't the version Google primarily ranks against. Field data tools typically report mobile and desktop Core Web Vitals separately.

---

# 9. Page Speed

Page speed is the broader discipline Core Web Vitals are a standardized subset of — encompassing server response time, resource loading, rendering efficiency, and overall time-to-interactive. `seo-playbook page-speed <url>` runs a static audit covering render-blocking resources, image/font issues, page weight, and a genuinely measured time-to-first-byte.

---

# 10. Render Blocking Resources

Render-blocking scripts and stylesheets delay LCP by forcing the browser to download and process them before painting any content. `seo-playbook page-speed` flags `<script>` tags in `<head>` missing `async`/`defer`, and an excessive count of render-blocking stylesheets. See [Chapter 4, Section 13](chapter-04.md).

---

# 11. Image Optimization

Images are frequently the largest assets on a page and a major LCP/CLS contributor. Use modern formats (WebP/AVIF), appropriate compression, explicit `width`/`height` attributes, and `loading="lazy"` for below-the-fold images specifically — all checked by `seo-playbook page-speed` and `seo-playbook audit`.

---

# 12. Font Optimization

Web fonts can delay text rendering (if render-blocking) or cause a layout shift when they swap in (if not). Use `font-display: swap` or `optional`, preload critical fonts, and limit the number of font weights/families loaded. `seo-playbook page-speed` flags Google Fonts stylesheets missing a `display=swap` parameter.

---

# 13. JavaScript Optimization

Minimize and defer non-critical JavaScript, split large bundles so only what's needed for the initial view loads first, and keep event handlers lightweight to protect INP. See [Chapter 4](chapter-04.md) for the full rendering pipeline JavaScript execution sits within.

---

# 14. CSS Optimization

Inline critical above-the-fold CSS, defer non-critical stylesheets, and eliminate unused CSS rules from the shipped bundle to reduce render-blocking time. See [Chapter 4, Section 17](chapter-04.md).

---

# 15. Lazy Loading

Defer loading of below-the-fold images and iframes with `loading="lazy"`, while ensuring above-the-fold, LCP-relevant content is never lazy-loaded (which would delay it further). `seo-playbook page-speed` flags pages with several images and none using lazy loading.

---

# 16. Browser Caching

Setting appropriate cache headers (`Cache-Control`, `ETag`) lets returning visitors' browsers reuse previously-downloaded assets instead of re-fetching them, meaningfully improving repeat-visit load times without any change to the assets themselves.

---

# 17. Content Delivery Networks (CDNs)

A CDN serves assets from edge locations geographically closer to the visitor, reducing latency and improving both TTFB and overall load time — particularly valuable for sites with a geographically distributed audience.

---

# 18. Performance Monitoring

Core Web Vitals should be monitored continuously via field data (real user visits), not just checked once at launch — performance can regress silently as new features, third-party scripts, or content are added over time. `seo-playbook site-audit` provides a repeatable way to check page-speed health across many URLs on a recurring basis.

---

# 19. Google PageSpeed Insights

PageSpeed Insights reports both field data (real Chrome User Experience Report data, where available) and lab data (a simulated Lighthouse run) for a given URL — field data is the actual ranking-relevant signal; lab data is useful for diagnosis even when field data isn't yet available for a new or low-traffic page.

---

# 20. Lighthouse

Lighthouse is the open-source auditing engine behind PageSpeed Insights' lab data (and available directly in Chrome DevTools), producing a detailed breakdown of performance opportunities and diagnostics beyond just the three Core Web Vitals themselves.

---

# 21. Chrome DevTools

Chrome DevTools' Performance and Lighthouse panels let you profile a page's loading behavior directly, throttle network/CPU to simulate real-world conditions, and pinpoint exactly which resources or scripts are contributing to slow LCP or poor INP.

---

# 22. Search Console Reports

Search Console's Core Web Vitals report aggregates field data across a site's pages, grouped by status (Good/Needs Improvement/Poor) and URL group — the most direct source of truth for which page types actually need performance attention at scale, rather than checking pages one at a time.

---

# 23. Common Performance Issues

- Unoptimized, oversized images with no lazy loading or explicit dimensions
- Render-blocking third-party scripts (analytics, ads, chat widgets) loaded synchronously
- Web fonts causing layout shift or delaying text render
- Heavy JavaScript execution delaying interactivity (poor INP)
- No caching or CDN, leaving every visit to fetch assets from scratch

---

# 24. Optimization Checklist

- [ ] LCP ≤ 2.5s, INP ≤ 200ms, CLS ≤ 0.1 in field data (CrUX/Search Console), not lab data alone
- [ ] Render-blocking scripts/stylesheets minimized — `seo-playbook page-speed`
- [ ] All images have explicit width/height and appropriate compression
- [ ] Below-the-fold images use `loading="lazy"`; above-the-fold content does not
- [ ] Web fonts use `font-display: swap` and are limited in count
- [ ] Core Web Vitals monitored continuously via Search Console, not checked once at launch

---

# 25. Best Practices

- Treat field data (real user visits) as the ranking-relevant signal; use lab data for diagnosis
- Fix the root cause behind a poor metric (slow TTFB, unoptimized images, heavy JS) rather than chasing the score directly
- Reserve space for every image and ad slot to prevent layout shift
- Defer non-critical JavaScript and CSS; keep only what's needed for the initial view synchronous
- Monitor Core Web Vitals continuously, since performance regresses silently as a site evolves

---

# Summary

Core Web Vitals turn "page experience" from a vague quality gesture into three concrete, field-measured metrics — LCP, INP, and CLS — each with specific, well-understood technical causes and fixes. They matter both as a modest ranking signal and, far more consequentially, as a direct driver of user satisfaction and conversion; `seo-playbook page-speed` and `site-audit` provide a free, scriptable way to catch the most common root causes before they show up as a field-data regression in Search Console.

---

# Learning Outcomes

After completing this chapter, you will understand:

- Core Web Vitals metrics
- Performance optimization techniques
- PageSpeed Insights
- Lighthouse auditing
- Improving user experience and SEO

---

# References

- Google Search Central: Understanding Core Web Vitals and Google Search Results
- web.dev: Core Web Vitals Documentation

---

**Next:** Chapter 14 – Structured Data & Schema Markup
