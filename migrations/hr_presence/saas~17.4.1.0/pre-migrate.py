from odoo.addons.base.maintenance.migrations import util


def migrate(cr, version):
    util.if_unchanged(cr, "hr_presence.mail_template_presence", util.update_record_from_xml)
    util.if_unchanged(cr, "hr_presence.sms_template_data_hr_presence", util.update_record_from_xml)
