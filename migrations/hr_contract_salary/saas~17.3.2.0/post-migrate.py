from odoo.upgrade import util


def migrate(cr, version):
    signatories_fields = [
        "sign_template_signatories_ids",
        "contract_update_signatories_ids",
    ]
    util.recompute_fields(cr, "hr.contract", signatories_fields)
