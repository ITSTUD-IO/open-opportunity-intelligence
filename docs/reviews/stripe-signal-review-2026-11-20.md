# Stripe signal review — 2026-11-20

## Review 1
- Posting: Senior Brand Designer, Link
- URL: https://stripe.com/jobs/search?gh_jid=8172672
- Board: greenhouse/stripe
- Detected category: cloud
- Matched term: `Cloud` (description)
- Human assessment: **false positive** (user-confirmed)
- Review status: labeled; full posting context not independently verified
- Note: A keyword match in a design job description does not by itself indicate a technical cloud initiative or consulting demand.
- Follow-up: Evaluate contextual exclusions and require stronger evidence before changing the rule; preserve this case as a regression fixture.

## Review 2
- Posting: Technical Recruiter, OpenRouter (Fixed Term)
- URL: https://stripe.com/jobs/search?gh_jid=8404144
- Board: greenhouse/stripe
- Detected category: architecture
- Matched term: `Architecture` (description)
- Human assessment: **false positive** (user-confirmed)
- Review status: labeled; full posting context not independently verified
- Note: Recruiting-role context does not substantiate an architecture initiative from the keyword alone.
- Follow-up: Preserve as regression fixture; consider role/context-aware classification rather than blanket keyword removal.

## Review 3
- Posting: Software Engineer, Secure Devices
- URL: https://stripe.com/jobs/search?gh_jid=7982720
- Board: greenhouse/stripe
- Detected categories: platform_engineering, cloud
- Matched terms: `platform engineering`, `cloud`, `AWS` (description)
- Human assessment: **both signals relevant** (user-confirmed)
- Review status: labeled; full posting context not independently verified
- Note: Technical signal relevance does not establish consulting buying intent.
- Follow-up: Preserve as positive regression fixture for both categories.

## Review 4
- Posting: Staff Backend Engineer - CI Services
- URL: https://stripe.com/jobs/search?gh_jid=8089815
- Board: greenhouse/stripe
- Detected categories: platform_engineering, devops, architecture
- Matched terms: `developer experience` (platform_engineering); `DevOps`, `CI/CD` (devops); `architecture` (architecture), all in description
- Human assessment: **all three signals relevant** (user-confirmed)
- Review status: labeled; full posting context not independently verified
- Follow-up: Preserve as positive regression fixture for all three categories. Relevance does not establish consulting buying intent.

## Review 5
- Posting: Integration Engineer, Professional Services
- URL: https://stripe.com/jobs/search?gh_jid=8203973
- Board: greenhouse/stripe
- Detected categories: cloud, devops, architecture, ai_engineering
- Matched terms: `cloud`, `CI/CD`, `architecture`, `LLM` (description)
- Human assessment: **all four signals relevant** (user-confirmed)
- Review status: labeled; full posting context not independently verified
- Follow-up: Preserve as positive regression fixture for all four categories. This is not evidence of external consulting buying intent.

## Review 6
- Posting: Implementation Consultant, Professional Services
- URL: https://stripe.com/jobs/search?gh_jid=8203977
- Board: greenhouse/stripe
- Detected categories: cloud, architecture, ai_engineering
- Matched terms: `cloud`, `architecture`, `LLM` (description)
- Human assessment: **all three signals relevant** (user-confirmed)
- Review status: labeled; full posting context not independently verified
- Follow-up: Preserve as positive regression fixture for all three categories; no inference of consulting buying intent.

## Review 7
- Posting: Staff Engineer, Support Experiences
- URL: https://stripe.com/jobs/search?gh_jid=8162185
- Board: greenhouse/stripe
- Detected categories: architecture, ai_engineering
- Matched terms: `architecture`, `LLM`, `generative AI` (description)
- Human assessment: **both signals relevant** (user-confirmed)
- Review status: labeled; full posting context not independently verified
- Follow-up: Preserve as positive regression fixture for both categories; no inference of consulting buying intent.

## Review 8
- Posting: Staff Product Manager, Sail Core
- URL: https://stripe.com/jobs/search?gh_jid=7913698
- Board: greenhouse/stripe
- Detected categories: platform_engineering, architecture
- Matched terms: `developer experience`, `architecture` (description)
- Human assessment: **both signals relevant** (user-confirmed)
- Review status: labeled; full posting context not independently verified
- Follow-up: Preserve as positive regression fixture for both categories; relevance does not establish consulting buying intent.

## Review 9
- Posting: Full Stack Engineer, Developer & End User Experience Platform
- URL: https://stripe.com/jobs/search?gh_jid=6567104
- Board: greenhouse/stripe
- Detected category: platform_engineering
- Matched term: `developer experience` (description)
- Human assessment: **platform_engineering relevant** (user-confirmed)
- Review status: labeled; full posting context not independently verified
- Follow-up: Preserve as positive regression fixture; relevance does not establish consulting buying intent.

## Review 10
- Posting: Security Engineer, Bridge
- URL: https://stripe.com/jobs/search?gh_jid=7776179
- Board: greenhouse/stripe
- Detected category: devops
- Matched term: `CI/CD` (description)
- Human assessment: **devops relevant** (user-confirmed)
- Review status: labeled; full posting context not independently verified
- Follow-up: Preserve as positive regression fixture; relevance does not establish consulting buying intent.

## Review 11
- Posting: Strategy & Transformation Advisor (Enterprise Commerce Architecture)
- URL: https://stripe.com/jobs/search?gh_jid=8139711
- Board: greenhouse/stripe
- Detected categories: architecture, cloud
- Matched terms: `Architecture` (title and description), `cloud` (description)
- Human assessment: **architecture and cloud relevant** (user-confirmed)
- Review status: labeled; full posting context not independently verified
- Follow-up: Preserve as positive regression fixture; distinguish Stripe's own demand from client-facing advisory work.

## Review 12
- Posting: Account Executive, Product Sales (Data)
- URL: https://stripe.com/jobs/search?gh_jid=8190059
- Board: greenhouse/stripe
- Detected categories: none (negative sample)
- Human assessment: **correct negative — no relevant technical signal** (user-confirmed)
- Review status: labeled; full posting context not independently verified
- Follow-up: Preserve as a negative regression fixture; absence of a signal is not proof that no technical initiatives exist.

## Review 13
- Posting: Account Executive, Startups - Grower (Italian Fluency)
- URL: https://stripe.com/jobs/search?gh_jid=8319823
- Board: greenhouse/stripe
- Detected categories: none (negative sample)
- Human assessment: **correct negative — no relevant technical signal** (user-confirmed)
- Review status: labeled; full posting context not independently verified
- Follow-up: Preserve as a negative regression fixture; absence of a signal is not proof that no technical initiatives exist.

## Review 14
- Posting: Third Party Risk Analyst
- URL: https://stripe.com/jobs/search?gh_jid=8189018
- Board: greenhouse/stripe
- Detected categories: none (negative sample)
- Human assessment: **correct negative — no relevant technical signal** (user-confirmed)
- Review status: labeled; full posting context not independently verified
- Follow-up: Preserve as a negative regression fixture; absence of a signal is not proof that no technical initiatives exist.

## Review 15
- Posting: Deal Pricing Strategist, APAC
- URL: https://stripe.com/jobs/search?gh_jid=7960875
- Board: greenhouse/stripe
- Detected categories: none (negative sample)
- Human assessment: **correct negative — no relevant technical signal** (user-confirmed)
- Review status: labeled; full posting context not independently verified
- Follow-up: Preserve as a negative regression fixture; absence of a signal is not proof that no technical initiatives exist.

## Review 16 (pending)
- Posting: Partner Development Manager- Alliances & Channels
- URL: https://stripe.com/jobs/search?gh_jid=8267519
- Board: greenhouse/stripe
- Detected categories: none (negative sample)
- Human assessment: pending
