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

Rebuilding an existing proposal reuses its folder and overwrites `index.html`, so the live URL never changes and links already emailed to a merchant keep working.

## How the site deploys

Every push to `main` runs `.github/workflows/pages.yml`, which uploads the repo as-is to GitHub Pages. No Jekyll, no processing.

This replaced GitHub's `legacy` Pages builder on 2026-08-06. The legacy builder hung on every build from 2026-08-05 16:40 UTC onward and froze the live site without any visible signal: newly published proposals returned 404, and rebuilt proposals kept serving their old version at a 200, which is worse because it looks fine.

**If a proposal URL 404s after publishing, check the deploy before touching the files:**

```powershell
gh run list --repo ChrisSM-APP/AllProPay-Proposals --workflow pages.yml --limit 3
gh run view <run-id> --repo ChrisSM-APP/AllProPay-Proposals --log-failed
```

## Removing a proposal

**Do not `git rm` a proposal folder that has been sent to a merchant.** Doing so 404s a link that is already sitting in someone's inbox. It has happened. If a proposal is dead, leave the folder serving and stop sending the link.

Only remove a folder that was never sent, for example a stray duplicate left by an old rebuild.
