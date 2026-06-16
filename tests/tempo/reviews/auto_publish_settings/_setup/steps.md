# Auto-publish Settings — Setup

Provisions the directory-scoped prerequisites for both scenarios via API (the
isolated runner account is not used — these scenarios need a business created
inside a directory). No UI login happens here; each test logs in as its own
business so it stays self-contained.

1. Provision the **no-review-site** triple (scenario 2):
   - Create a directory (Admin) with no external review site.
   - Create a business inside that directory (Platform API, directory token) and read it back by email.
   - Enable reviews + automation feature flags on the business.
   - Create a client for the business (capturing the client-portal JWT token).
2. Provision the **with-review-site** triple (scenario 3): same as above, but the
   directory is created with an external review site (`https://www.vcita.com`, label `vcita`).
3. Store both triples in the shared context (`auto_publish_no_site`,
   `auto_publish_with_site`) for the two tests to consume.
