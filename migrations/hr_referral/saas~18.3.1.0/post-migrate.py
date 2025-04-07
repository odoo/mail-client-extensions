from odoo.upgrade import util


def migrate(cr, version):
    util.update_record_from_xml(cr, "hr_recruitment.group_hr_recruitment_user", from_module="hr_referral")

    utm_source_referral = util.ref(cr, "utm.utm_source_referral")
    cr.execute(
        "UPDATE hr_applicant SET source_id = %s WHERE ref_user_id IS NOT NULL",
        [utm_source_referral],
    )
