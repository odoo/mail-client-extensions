from odoo.addons.base.maintenance.migrations import util


def migrate(cr, version):
    if util.version_gte("saas~13.1") and not util.module_installed(cr, "pos_iot"):
        # in pos_enterprise pos.config.is_posbox is now aliased as module_pos_iot,
        # when True the module pos_iot must be installed, but after uninstalling
        # iot module we may have a wrong False value
        cr.execute("UPDATE pos_config SET is_posbox = False WHERE is_posbox")
