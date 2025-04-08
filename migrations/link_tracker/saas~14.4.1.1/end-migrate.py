from odoo.upgrade import util


def migrate(cr, version):
    util.remove_constraint(cr, "link_tracker", "link_tracker_url_utms_uniq")
