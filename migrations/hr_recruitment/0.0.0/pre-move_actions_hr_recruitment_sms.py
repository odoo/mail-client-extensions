from odoo.addons.base.maintenance.migrations import util


def migrate(cr, version):
    eb = util.expand_braces
    if util.version_between("17.0", "19.0"):
        if util.module_installed(cr, "hr_recruitment_sms"):
            util.rename_xmlid(cr, *eb("hr_recruitment{,_sms}.action_hr_applicant_mass_sms"))
        else:
            util.delete_unused(cr, "hr_recruitment.action_hr_applicant_mass_sms")

    if util.version_between("18.0", "saas~18.1"):
        if util.module_installed(cr, "hr_recruitment_sms"):
            # Action `action_hr_candidate_mass_sms` was introduced in `18.0`
            # and it was removed in `saas~18.2`
            util.rename_xmlid(cr, *eb("hr_recruitment{,_sms}.action_hr_candidate_mass_sms"))
        else:
            util.delete_unused(cr, "hr_recruitment.action_hr_candidate_mass_sms")
