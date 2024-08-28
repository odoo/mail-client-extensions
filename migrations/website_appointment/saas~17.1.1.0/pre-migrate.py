from odoo.upgrade import util


def migrate(cr, version):
    util.remove_inherit_from_model(cr, "appointment.type", "website.cover_properties.mixin")
