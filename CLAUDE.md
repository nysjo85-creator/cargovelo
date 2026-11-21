# Working notes for Claude

See `README.md` for what this prototype is and how v1 and v2 are built.

## Publishing

- Pushing to `main` on `nysjo85-creator/cargovelo` deploys to GitHub Pages: https://nysjo85-creator.github.io/cargovelo/ (live about 1–2 minutes after a push).
- Git pushes authenticate through the GitHub CLI at `~/.local/bin/gh` (`gh auth setup-git`). GitHub Desktop works on the same folder too.
- Jo is new to GitHub: explain git steps in plain words.

## Editing v2

- Don't hand-edit the generated pages under `v2/`. Edit `tools/v2_onepage.html` or `tools/build_v2.py`, then run `python3 tools/build_v2.py`, and commit the source and the regenerated pages together.
- Preview locally with `python3 -m http.server 8000` before pushing.
- Site copy is in Dutch (Flemish), built around *ontzorgen*.
