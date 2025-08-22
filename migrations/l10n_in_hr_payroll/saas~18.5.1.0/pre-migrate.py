from odoo.upgrade import util


def migrate(cr, version):
    xmlid = "l10n_in_hr_payroll.l10n_in_contract_type_intern"
    intern = util.ref(cr, "hr.contract_type_intern")
    if intern is not None:
        util.replace_record_references_batch(cr, {util.ref(cr, xmlid): intern}, "hr.contract.type", replace_xmlid=False)
        util.remove_record(cr, xmlid)
    else:
        util.delete_unused(cr, xmlid)
