# -*- coding: utf-8 -*-
import logging

from odoo.addons.base.maintenance.migrations import util


def migrate(cr, version):
    if not util.version_gte("saas~13.5"):
        return

    # As these dynamic views can be added after the release[^1], it should not block upgrade of databases
    # created before the bugfix that introduce the dynamic view.
    # Just adapt the log level depending on the environment.
    # [^1]: https://github.com/odoo/odoo/pull/75651
    level = logging.CRITICAL if util.on_CI() else logging.WARNING

    env = util.env(cr)
    for name in env:
        model = env[name]

        # avoid calling the `_table_query` property (if defined) as it can be costly and/or needs a specific context
        dynamic_view = not isinstance(type(model)._table_query, type(None))

        if dynamic_view and util.table_exists(cr, model._table):
            msg = "Model {0._name!r} is defined as a dynamic view, but the view {0._table!r} still exists".format(model)
            util._logger.log(level, msg)
