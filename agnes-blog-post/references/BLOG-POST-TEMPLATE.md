# Blog Post Template

Use this as the starting template when creating a new blog post.

## Template

```markdown
---
title: "TITLE_HERE"
description: "DESCRIPTION_HERE"
authors:
  - AUTHOR_KEY_HERE
---

![blog banner](banner.png)

INTRO_PARAGRAPH_HERE

<!--truncate-->

## First Section

Content here...

## Second Section

Content here...

## Wrapping Up

Conclusion and call-to-action here...

<head>
  <meta property="og:title" content="TITLE_HERE" />
  <meta property="og:type" content="article" />
  <meta property="og:url" content="https://kiwiar-ai.github.io/agnet-skills/blog/YYYY/MM/DD/slug-title" />
  <meta property="og:description" content="DESCRIPTION_HERE" />
  <meta property="og:image" content="https://kiwiar-ai.github.io/agnet-skills/assets/images/FILENAME_FROM_PREVIEW" />
  <meta name="twitter:card" content="summary_large_image" />
  <meta property="twitter:domain" content="kiwiar-ai.github.io" />
  <meta name="twitter:title" content="TITLE_HERE" />
  <meta name="twitter:description" content="DESCRIPTION_HERE" />
  <meta name="twitter:image" content="https://kiwiar-ai.github.io/agnet-skills/assets/images/FILENAME_FROM_PREVIEW" />
</head>
```

## Author Entry Template

Add to `authors.yml` if the author doesn't exist:

```yaml
authorkey:
  name: Full Name
  title: Job Title
  image_url: https://avatars.githubusercontent.com/u/GITHUB_USER_ID?v=4
  page: true
  socials:
    github: github-username
    x: x-username
    linkedin: linkedin-username
```

## Frontmatter Quick Reference

| Field | Required | Notes |
|-------|----------|-------|
| `title` | Yes | Wrap in quotes, title case |
| `description` | Yes | 1-2 sentences, used for SEO and social previews |
| `authors` | Yes | YAML list of keys from `authors.yml` |
| `date` | No | **Do not include** — derived from directory name |
| `tags` | No | **Do not include** — not used on this blog |

## Directory Naming

```
YYYY-MM-DD-slug-title/
├── index.md
└── banner.png   (1200×600, required — also used for social sharing)
```

## `<head>` Section (Required)

Placed at the very end of `index.md`. The `og:image` and `twitter:image` URLs
must be obtained from the local preview (see SKILL.md Step 6).

## Key URLs

- agnes docs: https://kiwiar-ai.github.io/agnet-skills/
- agnet-skills repo: https://github.com/AgnesAI-Labs/agnet-skills-cn
- Extensions directory: https://kiwiar-ai.github.io/agnet-skills/extensions
- MCP docs: https://modelcontextprotocol.io/introduction

## Image URL Discovery

1. Run `npm start` in `<agnet-skills-repo>/documentation/` (separate terminal)
2. Navigate to blog post in browser
3. Right-click banner image → Copy Image Address
4. Extract filename (e.g., `banner-a1b2c3d4e5f6.png`)
5. Production URL: `https://kiwiar-ai.github.io/agnet-skills/assets/images/<filename>`
