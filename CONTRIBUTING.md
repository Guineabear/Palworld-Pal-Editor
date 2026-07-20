# Contributing to Paldeck

Paldeck is a community-maintained GPL-3.0 project. Small, focused pull requests are welcome.

## Development setup

1. Install Python 3.11 or newer and Node.js.
2. Create a virtual environment and run `python -m pip install -e .`.
3. In `frontend/palworld-pal-editor-webui`, run `npm ci` and `npm run dev`.
4. Run the backend with `python -m palworld_pal_editor`.

## Before submitting

- Never test writes against the only copy of a world. Copy the complete world folder first.
- Run `python -m unittest discover -s tests`, `python -m compileall src`, and `npm run build`.
- Keep save-format compatibility in the Python layer and presentation changes in Vue.
- Do not invent meanings for undocumented game fields. Label uncertain content experimental.
- Preserve GPL attribution and describe new save fields with a source or reproducible save comparison.

## Pull requests

Explain the affected Palworld version, include a minimal reproduction, and describe the save round trip used for validation. Do not attach private player saves to public issues.
