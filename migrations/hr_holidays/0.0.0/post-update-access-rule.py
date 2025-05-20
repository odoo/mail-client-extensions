from odoo.addons.base.maintenance.migrations import util


def migrate(cr, version):
    # the noupdate record was modified but not updated
    if util.version_between("saas~18.1", "19.0"):
        util.update_record_from_xml(cr, "hr_holidays.hr_holidays_status_rule_multi_company")
