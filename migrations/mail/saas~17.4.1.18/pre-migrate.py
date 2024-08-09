from odoo.upgrade import util


def migrate(cr, version):
    util.remove_field(cr, "mail.message", "description")

    # payload format has changed and new format is incompatible with
    # previous payload format, so discard existing bus notifications
    cr.execute("TRUNCATE bus_bus")
