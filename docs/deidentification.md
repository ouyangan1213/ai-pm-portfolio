# De-identification

This repository is public. It was written from scratch (no history copied from private repositories) and follows these rules.

## Not included
- Employer name (described only as "a bioreagent company"), customer or account names, colleague names; combinations of team size, regions and exact dates that could identify the employer
- Sales, order, pricing or contact data from the company; account counts by customer
- Email addresses, access codes, tokens, workspace or app identifiers, keys
- Server addresses, host names, ports of live services, internal file paths
- Production code; competitor vendor names; internal product names

## What is included
- Scale and quality metrics rounded to orders of magnitude (e.g. "60+ sellers", "~30k items"); no exact internal counts
- Architecture and decisions, described generically
- Skeletons and pseudocode written for this repository, using synthetic data (`Account Alpha`, `Target A`, `Kit Z`, `Vendor X`, `*.example` domains)
- Names of public platforms and models in generic terms

## How it was checked
1. Author self-scan against a private list of sensitive terms (kept outside this repository) plus generic patterns for emails, IP addresses, URLs, tokens and absolute paths.
2. Independent read-only review by a separate auditing agent, required to report zero hits before publication.
