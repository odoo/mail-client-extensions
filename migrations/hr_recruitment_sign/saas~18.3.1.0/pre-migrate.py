from odoo.upgrade import util


def migrate(cr, version):
    util.remove_field(cr, "hr.recruitment.sign.document.wizard", "applicant_id")
    util.remove_field(cr, "hr.recruitment.sign.document.wizard", "partner_id")
    util.remove_field(cr, "hr.recruitment.sign.document.wizard", "partner_name")

    eb = util.expand_braces
    util.rename_xmlid(cr, *eb("hr_recruitment_sign.{action_request_signature,action_signature_request_multi}"))
