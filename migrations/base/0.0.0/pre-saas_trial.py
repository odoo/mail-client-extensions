# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util


def migrate(cr, version):
    # This assets bundle is loaded as a view before saas-14.3 via
    # the saas_trial/views/assets.xml. With the new assets system in saas-14.3,
    # those views are converted to ir.assets records but they conflict with newest version
    # of those assets that better handle the newer JS frameworks (owl 1+)
    if util.version_gte("saas~14.3"):
        util.remove_record(cr, "saas_trial.assets_common")
        if util.table_exists(cr, "ir_asset"):
            path_field_name = "path" if util.column_exists(cr, "ir_asset", "path") else "glob"
            cr.execute(
                util.format_query(
                    cr,
                    """
                    DELETE FROM ir_asset
                     WHERE name LIKE 'saas_trial.assets_common%'
                       AND bundle = 'web.assets_common'
                       AND {} = '/saas_trial/static/js/activation.js'
                    """,
                    path_field_name,
                )
            )

    # Avoid view being deativated by the view verification post test.
    util.remove_view(cr, "saas_trial.paid_apps_module_kanban")
    util.remove_view(cr, "saas_trial.paid_apps_module_form")
