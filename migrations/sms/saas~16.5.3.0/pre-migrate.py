from odoo.upgrade import util


def migrate(cr, version):
    util.create_column(cr, "sms_sms", "uuid", "varchar(32)", default=None)

    util.remove_model(cr, "sms.api")

    cr.execute("DROP INDEX IF EXISTS mail_notification_sms_id_fkey")
    util.rename_field(cr, "mail.notification", "sms_id", "sms_id_int")
