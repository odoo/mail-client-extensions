from odoo.upgrade import util


def migrate(cr, version):
    util.remove_field(cr, "hr.referral.campaign.wizard", "sending_method")
    util.remove_field(cr, "hr.referral.campaign.wizard", "sms_body")
    util.remove_record(cr, "hr_referral.action_hr_job_launch_referral_campaign")
