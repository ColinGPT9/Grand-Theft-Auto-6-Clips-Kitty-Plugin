# Prepared marketplace contribution

Display name: **Grand Theft Auto 6 Clips Kitty Plugin**. Catalog kind:
`pipeline`; existing section: `gaming/grand-theft-auto`. The manifest is
the source for the name, description, MIT license, stages, compatibility,
permissions, and game names. The catalog file only identifies the repository,
immutable version, section, and search aliases.

The draft is [listing.template.yaml](listing.template.yaml). Its commit
marker deliberately prevents installation. It is **not** a valid published
listing and must not be copied into the live registry unchanged.

## Source and schema

Reviewed the actual Awesome Clips Kitty repository at
`cf3b87a88fe3b44017a5eaabbb991f9746509559`, including `CONTRIBUTING.md`,
`registry/sections.yaml`, the existing scene-cut listing, and Clips Kitty's
`sdk/python/clipskitty_sdk/listing.py` plus `plugins/registry.py`. The
contribution path is:

```text
registry/pipelines/colingpt9/gta-vi-highlights.yaml
```

No second registry or generated `index.json` was created. The catalog's
instructions call for a one-file pull request; its workflow regenerates
the catalog README and index. The SDK listing module contains an outdated
docstring saying generated files must be included, but its current printed
instructions and the actual catalog contribution guide agree on one file.

The confirmed repository is
`https://github.com/ColinGPT9/Grand-Theft-Auto-6-Clips-Kitty-Plugin`.
The owner completed the rename, verified through GitHub's API on 2026-10-25.
Verify the immutable release commit before generating the real listing.

## Generate after release preparation

1. Run the real SDK validator and appropriate plugin tests. Keep the tested
   manifest/source and version together.
2. Review the complete diff, commit that exact source, and make the commit
   public in the actual repository. A release tag is useful; the catalog
   requires the immutable full commit hash.
3. From the tested plugin directory, with SDK 1.3.0 available, run:

   ```bash
   python -m clipskitty_sdk validate .
   python -m clipskitty_sdk listing . \
     --section gaming/grand-theft-auto \
     --alias 'GTA 6' --alias 'GTA VI' --alias 'GTA V' --alias 'GTA highlights' \
     --out /tmp/gta-vi-highlights-listing.yaml
   ```

   The SDK intentionally writes outside the plugin installation folder.
   It checks for a clean, committed plugin and a pushed remote-tracking
   branch. That local branch check does not replace the registry's public
   manifest fetch and repository reachability verification.
4. In a reviewed checkout of `ColinGPT9/awesome-clips-kitty`, copy the
   generated file to the path above. Build/check with the actual host
   registry tools. Do not replace the draft marker by an unrelated old
   commit or a made-up hash.
5. Prepare a one-file catalog pull request when publication is authorized.
   Do not claim `checked`, compatible, featured, installs, or live footage
   accuracy without the corresponding actual maintainer/compatibility
   evidence. Catalog data is CC0-1.0; the plugin remains MIT.

The registry fetches `clipskitty.yaml` at that commit and requires it to
be reachable on the named repository's own branch/tag. A locally modified
plugin or commit not containing the manifest cannot be made installable
by a plausible YAML file.

## Validation boundaries

Static draft field validation can check the real section, ID/path pairing,
repository owner, aliases, version syntax, and required full-hash shape.
The intentional marker must be rejected by the real validator. Final
manifest-at-commit, public reachability, installed host execution, and
real source quality remain separate checks. No publication or catalog PR
has been performed by this preparation.

The listing description should describe an unofficial evidence-based
GTA-style SDK plugin and host-provided Twitch/Discord catch-up integration.
It must disclose that GTA VI accuracy and footage quality are unverified
until real footage is evaluated. Include installation/settings/limitations
from the final README and only rights-cleared screenshots or example clips.
