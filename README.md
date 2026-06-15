# AllProPay-Proposals

Public hosting for AllProPay merchant proposal pages.

**Live at:** https://proposals.allpropay.com

## How it works

- Each proposal lives at `proposals.allpropay.com/{merchant-slug}-{random}/`
- The random suffix keeps URLs hard to guess (security through obscurity)
- The root URL shows a generic landing page — proposals are not listed or linked
- `noindex, nofollow` meta tag on the landing page keeps it out of search engines

## Publishing a new proposal

The statement-analyzer skill in `AllProPay Sales/statement-analyzer/` handles publishing automatically. It copies the rendered HTML proposal to a new folder here, commits, pushes, and returns the shareable URL.

## Validating proposals

Since this is a static site, the "test suite" guards against publishing
regressions — broken logos, unfilled placeholders, missing `noindex`, stray
third-party dependencies. Run it before pushing:

```bash
python3 scripts/validate_proposals.py
```

It checks every `*/index.html` for: resolvable local links/assets, required
structure (`DOCTYPE`, `<html lang>`, non-empty `<title>`, viewport), a
`noindex,nofollow` robots meta, use of the shared `assets/` logo (no
per-proposal copies), and an allowlist of external origins. CI runs the same
check on every push/PR via `.github/workflows/validate.yml`, and a Claude Code
`SessionStart` hook runs it automatically in web sessions.

## Removing a proposal

```powershell
cd C:\Users\Chris\GitHubAllProPay\AllProPay-Proposals
git rm -r "{merchant-slug}-{random}"
git commit -m "Remove {merchant-slug}"
git push
```

GitHub Pages will stop serving the URL within ~1 minute.
