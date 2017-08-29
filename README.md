This repository contains the migration scripts written to pass from version 7.0
to version 11.0 (to be continued...).

They are written incrementally as we deploy snapshots to the SaaS platform.

To use these migration scripts against `saas~*` versions, you have to symlink
this directory to:

```sh
$OPENERP_SERVER/odoo/addons/base/maintenance
```
