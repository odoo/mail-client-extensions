from odoo.upgrade import util


def migrate(cr, version):
    util.create_column(cr, "ir_act_server", "sms_method", "varchar")
    cr.execute(
        """
            UPDATE ir_act_server
               SET sms_method = CASE WHEN sms_mass_keep_log = true THEN 'note'
                                     ELSE 'sms'
                                     END
             WHERE state = 'sms'
        """
    )
    util.remove_field(cr, "ir.actions.server", "sms_mass_keep_log")
