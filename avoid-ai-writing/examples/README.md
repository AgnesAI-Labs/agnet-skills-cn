# House-style configuration examples

`prose.json` and `technical.json` are editable examples of the optional `--style` configuration. Copy a file and adjust its `register` and `mechanics` for your own writing context. They are general examples, not official style guides.

Pass a configuration path with `--style`, for example `--style examples/technical.json`. The Skill applies register guidance and the selected mechanics; only the subset documented by the Skill's checker can be verified mechanically. The remaining guidance depends on the model's judgment.

To check a prose file against a configuration, run this optional command from the Skill directory:

```bash
node scripts/check-style.js draft.md --config examples/technical.json
```

This package does not include the upstream repository's test suite. Node.js is needed only for the optional local checker and quote-normalization scripts; ordinary rewrite and detect requests do not require them.
