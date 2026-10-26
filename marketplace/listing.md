# Awesome Clips Kitty listing

The installable catalog entry belongs at
`registry/pipelines/colingpt9/gta-vi-highlights.yaml` in
[Awesome Clips Kitty](https://github.com/ColinGPT9/awesome-clips-kitty).
It uses the existing `gaming/grand-theft-auto` section.

The obsolete placeholder listing was removed. Generate the actual entry only
from the tested, committed, public plugin release:

```bash
python -m clipskitty_sdk validate .
python -m clipskitty_sdk listing . --section gaming/grand-theft-auto --alias 'GTA 6' --alias 'GTA VI' --alias 'GTA V' --alias 'GTA highlights' --out /tmp/gta-listing.yaml
```

The real entry pins a full immutable commit and version. Keep that pin in the
catalog, rather than embedding a self-referential release hash in this source.
Submit one YAML file; catalog CI fetches its public manifest without executing
plugin code, and the post-merge job generates README/index.json.

The plugin is MIT; catalog data is CC0-1.0. Do not mark the entry compatible,
featured or checked without the corresponding maintainer evidence.

A catalog entry does not update an old installed Store app. The catalog's own
rules reserve additions from the project's repositories for a bundled app
release. Direct source installation is documented in the README for a
compatible host. Store packaging and uploads are outside this task.
