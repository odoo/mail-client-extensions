from odoo.addons.base.maintenance.migrations import util


def migrate(cr, version):
    if util.version_between("16.0", "19.0"):
        util.update_record_from_xml(cr, "base.tr")
