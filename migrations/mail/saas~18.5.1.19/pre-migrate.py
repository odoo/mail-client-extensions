from odoo import modules

from odoo.upgrade import util


def migrate(cr, version):
    util.remove_field(cr, "res.users.settings", "mute_until_dt")
    util.remove_record(cr, "mail.ir_cron_discuss_users_settings_unmute")
    util.remove_field(cr, "res.partner", "starred_message_ids")

    template_lang_default_values = (
        "{{ object.partner_id.lang }}",
        "{{ object.partner_id.lang or '' }}",
        "{{ object._mail_get_customer().lang }}",  # saas~18.1+ databases
        "{{ object._get_mail_partner().lang }}",  # older databases
    )
    cr.execute(
        """
        WITH records AS (
      SELECT res_id
        FROM ir_model_data
       WHERE model = 'mail.template'
         AND module IN %s
        )
      UPDATE mail_template m
         SET lang = NULL
        FROM records
       WHERE m.id = records.res_id
         AND lang IN %s
        """,
        [tuple(modules.get_modules()), template_lang_default_values],
    )
