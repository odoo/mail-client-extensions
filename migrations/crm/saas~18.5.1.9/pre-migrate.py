from odoo.upgrade import util


def migrate(cr, version):
    util.convert_m2o_field_to_m2m(cr, "crm.stage", "team_id")
