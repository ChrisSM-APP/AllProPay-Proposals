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

## Removing a proposal

```powershell
cd C:\Users\Chris\GitHubAllProPay\AllProPay-Proposals
git rm -r "{merchant-slug}-{random}"
git commit -m "Remove {merchant-slug}"
git push
```

GitHub Pages will stop serving the URL within ~1 minute.
