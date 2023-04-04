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
            cr.execute(
                """
                DELETE FROM ir_asset
                WHERE name LIKE 'saas_trial.assets_common%'
                AND bundle = 'web.assets_common'
                AND path = '/saas_trial/static/js/activation.js'
                """
            )
