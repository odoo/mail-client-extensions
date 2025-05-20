from odoo.upgrade import util


def migrate(cr, version):
    util.rename_field(cr, "fleet.vehicle", "first_contract_date", "contract_date_start")
