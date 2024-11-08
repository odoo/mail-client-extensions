from odoo.addons.base.maintenance.migrations import util


def migrate(cr, version):
    util.remove_field(cr, "event.event", "has_lead_request")
