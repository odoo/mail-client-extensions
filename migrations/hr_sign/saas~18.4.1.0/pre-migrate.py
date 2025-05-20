from odoo.upgrade import util


def migrate(cr, version):
    util.rename_field(cr, "hr.contract.sign.document.wizard", "contract_id", "version_id")
