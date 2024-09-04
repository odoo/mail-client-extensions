from odoo.upgrade import util


def migrate(cr, version):
    # The `iot.channel` model switch from a Model to an AbstractModel
    # The value inside it should be already moved to a System Parameter (SP)
    # so we can safely remove it.
    # If it contains values, it means that the table was not used so we can remove it anyway.
    util.remove_model(cr, "iot.channel")
