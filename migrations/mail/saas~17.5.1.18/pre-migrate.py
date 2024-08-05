from odoo.upgrade import util


def migrate(cr, version):
    util.if_unchanged(cr, "mail.ir_cron_send_scheduled_message", util.update_record_from_xml)
