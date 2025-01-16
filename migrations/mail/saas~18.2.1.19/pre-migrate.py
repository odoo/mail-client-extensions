from odoo.upgrade import util


def migrate(cr, version):
    util.remove_field(cr, "discuss.channel", "allow_public_upload")
    util.remove_field(cr, "discuss.channel.member", "fold_state")
    util.remove_model(cr, "mail.wizard.invite")
    util.remove_field(cr, "res.config.settings", "tenor_content_filter")
    util.remove_field(cr, "res.config.settings", "tenor_gif_limit")

    eb = util.expand_braces
    util.rename_xmlid(cr, *eb("mail.account_security_{setting_update,alert}"))

    cr.execute(
        """
        DELETE FROM ir_config_parameter
              WHERE key IN ('discuss.tenor_content_filter', 'discuss.tenor_gif_limit')
        """
    )
