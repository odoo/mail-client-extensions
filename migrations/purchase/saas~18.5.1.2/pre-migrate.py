from odoo.upgrade import util


def migrate(cr, version):
    util.remove_field(cr, "res.company", "po_lead")
    util.remove_field(cr, "res.config.settings", "po_lead")
    util.remove_field(cr, "res.config.settings", "use_po_lead")
    cr.execute("DELETE FROM ir_config_parameter WHERE key='purchase.use_po_lead'")
