# -*- coding: utf-8 -*-

from odoo.upgrade import util


def migrate(cr, version):
    # remove global alias configuration
    util.remove_field(cr, "res.config.settings", "crm_alias_prefix")
    util.remove_field(cr, "res.config.settings", "generate_lead_from_alias")
    # remove alias xml ID but keep data as it may be used; only configuration is removed
    cr.execute(
        """
            DELETE
              FROM ir_model_data
             WHERE module = 'crm'
               AND name = 'mail_alias_lead_info'
        """
    )
