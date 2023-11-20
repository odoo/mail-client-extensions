from odoo.upgrade import util


def migrate(cr, version):
    util.remove_field(cr, "fleet.vehicle", "contract_renewal_total")
    util.remove_field(cr, "fleet.vehicle", "contract_renewal_name")
