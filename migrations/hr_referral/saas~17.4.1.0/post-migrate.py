from odoo.upgrade import util


def migrate(cr, version):
    util.update_record_from_xml(cr, "hr_referral.hr_referral_points_officer_rule")
