from odoo.upgrade import util


def migrate(cr, version):
    util.remove_field(cr, "res.users.settings", "mute_until_dt")
    util.remove_record(cr, "mail.ir_cron_discuss_users_settings_unmute")
    util.remove_field(cr, "res.partner", "starred_message_ids")
