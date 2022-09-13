> **Warning** Please **follow** and [check](https://docs.github.com/en/issues/tracking-your-work-with-issues/about-task-lists#creating-task-lists) the relevant boxes for your PR, otherwise the review may take longer.

For a PR that adds a _new_ upgrade script (for the Odoo's `master` branch or one of the RR versions):
- [ ] I've added the references to the Enterprise and/or Community PRs *in the commit message*, even if they are already merged.
- [ ] I've added an overall description of the changes made in the Community/Enterprise branches.

For a PR that _fixes_ an issue on an already existing upgrade script:
- [ ] I've added a clear description of the issue including information on how to reproduce it.
- [ ] I've tested the fix and included references of upgrade requests where this fix will be applicable in the form of `upg-<request_number>`.
- [ ] I've included references to the `OPW`, if applicable, in the form of `opw-<ticket_number>`.
- [ ] I've tested this fix on other DBs, not just the ones with the issue.

For _all_ PRs:
- [ ] My commit's title follows the [right format](https://github.com/odoo/upgrade/wiki/commit-message).
- [ ] My commit's body includes information about the changes.
- [ ] I've added `odoo/upgrade` as a reviewer.
- [ ] I've read and understood this list.
- [x] I will ensure all the CI checks are green.

> **Note** More info can be found [in the wiki](https://github.com/odoo/upgrade/wiki/How-To).
