# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util


def migrate(cr, version):
    if not util.version_gte("saas~13.5"):
        return

    env = util.env(cr)
    for name in env:
        model = env[name]

        # avoid calling the `_table_query` property (if defined) as it can be costly and/or needs a specific context
        dynamic_view = not isinstance(type(model)._table_query, type(None))

        if dynamic_view and util.table_exists(cr, model._table):
            msg = "Model {0._name!r} is defined as a dynamic view, but the view {0._table!r} still exists".format(model)
            if util.on_CI():
                raise util.MigrationError(msg)
            else:
                # As these dynamic views can be added after the release[^1], it should not block upgrade of databases
                # created before the bugfix that introduce the dynamic view.
                # [^1]: https://github.com/odoo/odoo/pull/75651
                util._logger.warning(msg)
