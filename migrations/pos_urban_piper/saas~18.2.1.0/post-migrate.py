from odoo.upgrade import util


def migrate(cr, version):
    cr.execute(
        """
        UPDATE res_company
           SET pos_urbanpiper_username = (SELECT value FROM ir_config_parameter WHERE key = 'pos_urban_piper.urbanpiper_username'),
               pos_urbanpiper_apikey = (SELECT value FROM ir_config_parameter WHERE key = 'pos_urban_piper.urbanpiper_apikey')
        """
    )
    # Remove config parameters; now useless.
    cr.execute(
        """
        DELETE FROM ir_config_parameter
        WHERE key IN ('pos_urban_piper.urbanpiper_username', 'pos_urban_piper.urbanpiper_apikey')
        """
    )
    util.remove_column(cr, "res_config_settings", "urbanpiper_username")
    util.remove_column(cr, "res_config_settings", "urbanpiper_apikey")
