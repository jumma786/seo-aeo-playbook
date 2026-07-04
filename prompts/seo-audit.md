# SEO Audit Prompts

For interpreting and prioritizing the *output* of an audit — `seo-playbook audit`, `page-speed`, and `site-audit` do the actual mechanical checking. These prompts help triage what they find.

## 1. Issue Prioritization

```
Here is a list of issues found by an SEO audit: {{paste issues, e.g. from
`seo-playbook site-audit urls.txt`}}. Group them into: fix immediately (blocking
indexing/ranking), fix this sprint (real but not urgent), and low priority (nice-to-have).
Briefly justify each grouping.
```

**When to use:** After running `seo-playbook site-audit` or `audit` across many pages, to turn a raw issue list into a work plan.

## 2. Root Cause Narrative

```
This page scored {{score}}/100 on an SEO audit with these flagged issues: {{list}}.
Write a 3-4 sentence plain-language summary of why this page is likely underperforming,
suitable for sharing with a non-technical stakeholder.
```

**When to use:** Translating audit output for stakeholders who don't need the raw issue list.

## 3. Traffic Drop Diagnostic

```
Organic traffic to {{page/section}} dropped {{%}} starting around {{date}}. Here's what
changed around that time: {{list any deploys, content edits, algorithm update dates}}.
Here's the current audit state: {{paste audit output}}. What's the most likely explanation,
and what would I check next to confirm it?
```

**When to use:** Working through the "traffic drop diagnostic process" recommended in the [Technical SEO Checklist](../checklists/technical-seo.md) and SEO Book Chapter 20.

## 4. Pre-Migration Risk Assessment

```
I'm migrating {{describe: domain change / URL structure change / CMS change}}. Here is my
current top-page list by traffic: {{list}}. What are the highest-risk failure modes for
this specific type of migration, and what should be in my redirect-map QA checklist?
```

**When to use:** Planning a site migration — pairs with the [Launch Checklist](../checklists/launch-checklist.md).

## 5. Recurring Audit Cadence Plan

```
My site has {{approximate page count}} pages across {{describe site type}}. Suggest a
realistic recurring audit cadence (what to check daily/weekly/monthly/quarterly) that
wouldn't be excessive for a team of {{team size}}.
```

**When to use:** Setting up ongoing monitoring rather than one-off audits — `seo-playbook site-audit` and `check-links` are both suited to being run on a schedule in CI.
