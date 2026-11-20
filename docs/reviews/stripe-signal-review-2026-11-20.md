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

## Review 5 (pending)
- Posting: Integration Engineer, Professional Services
- URL: https://stripe.com/jobs/search?gh_jid=8203973
- Board: greenhouse/stripe
- Detected categories: cloud, devops, architecture, ai_engineering
- Matched terms: `cloud`, `CI/CD`, `architecture`, `LLM` (description)
- Human assessment: pending
