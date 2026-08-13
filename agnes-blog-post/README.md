# agnes-blog-post

A skill that guides AI agents through writing and publishing blog posts for the [AgnesAI-Labs/agnet-skills-cn](https://github.com/AgnesAI-Labs/agnet-skills-cn) open source project.

## Installation

```bash
npx skills add https://github.com/AgnesAI-Labs/agnet-skills-cn --skill agnes-blog-post
```

## What It Does

- Scaffolds blog post directories with correct naming conventions and frontmatter
- Supports three modes: review your draft, expand your notes, or write from scratch
- Handles author setup in `authors.yml`
- Generates required `<head>` section with Open Graph and Twitter metadata
- Walks through local preview to obtain the hashed image URL
- Runs a final review checklist before publishing

See [SKILL.md](./SKILL.md) for full documentation.
