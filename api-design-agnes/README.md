# API Design for Agnes

`api-design-agnes` helps design and review REST API contracts. It covers resource paths, HTTP methods and status codes, request and response shapes, pagination, filtering, authentication and authorization, rate limiting, compatibility, and versioning.

## When to use it

- Design endpoints for a new REST API.
- Review an existing API contract for correctness, consistency, and security gaps.
- Choose a pagination or versioning strategy from stated product constraints.
- Turn business requirements into a concrete request, response, and error contract.

It is not a substitute for implementation testing, penetration testing, performance measurement, legal requirements, or a product's published compatibility policy.

## How to call it

Explicit invocation:

```text
Use api-design-agnes to design a partner-facing order API. Results may exceed one million rows, every order belongs to a merchant, and clients need incremental synchronization. Give me paths, parameters, cursor pagination, errors, authorization, rate limiting, and compatibility decisions. Mark assumptions clearly.
```

Natural-language request:

```text
Review this endpoint design. GET /api/v1/getOrders returns 200 for errors, has no pagination, and checks only that a token exists without verifying merchant ownership.
```

## Input

Provide as much of the following as is known:

- the business resources and user actions;
- whether the API is internal, public, or partner-facing;
- expected data size and access patterns;
- authentication and tenant/ownership rules;
- existing clients and compatibility commitments;
- traffic, availability, regulatory, or contractual constraints.

Missing details do not prevent a first draft. The Skill should ask only for facts that materially change the design or label its assumptions.

## Output

Depending on the request, the output may include:

- resource paths and HTTP methods;
- request parameters and schemas;
- success and error responses;
- authentication and resource-level authorization rules;
- offset or cursor pagination decisions;
- filtering, sorting, rate limits, and retry behavior;
- versioning, deprecation, and unresolved decisions;
- a prioritized review with consequences and minimal corrections.

All numeric limits, dataset thresholds, supported-version counts, and deprecation periods shown in examples are illustrative. Real values must come from the user's system, measurements, customer commitments, or governing policy.

## Dependencies and permissions

The core Skill is text-only. It requires no external API, account, credential, command-line tool, network request, file write, or persistent state. If a user separately asks Agnes to inspect project files, that access depends on the tools and permissions available in the user's Agnes environment.

## Source, license, and changes

Based on [`api-design`](https://github.com/affaan-m/ECC/tree/d2ef2680594f9a17526a6e1a2e18b3d242c5d17b/.agents/skills/api-design) by Affaan Mustafa. The locked upstream baseline is commit `d2ef2680594f9a17526a6e1a2e18b3d242c5d17b`, checked on 2026-11-09.

This Agnes edition:

- adds a context-first workflow and explicit design/review output contract;
- prioritizes authorization and correctness during reviews;
- clarifies that example limits, thresholds, version counts, and timelines are not universal defaults;
- adds clearer activation and non-activation boundaries;
- changes the invocation name to `api-design-agnes`.

The package is distributed under the upstream MIT license. See [`LICENSE`](LICENSE) for the complete text and copyright notice.
