from odoo.upgrade import util


def migrate(cr, version):
    util.remove_model(cr, "voip.configurator")
    util.rename_field(cr, "voip.phonecall", "phonecall_type", "direction")
