from odoo.addons.base.maintenance.migrations import util


def migrate(cr, version):
    if util.version_between("saas~14.4", "19.0"):
        util.remove_constraint(cr, "link_tracker", "link_tracker_url_utms_uniq", warn=False)
