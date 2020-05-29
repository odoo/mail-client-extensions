# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util


def migrate(cr, version):
    cr.execute(
        """
        UPDATE account_journal j
           SET invoice_reference_type = CASE c.l10n_be_structured_comm
                                             WHEN 'partner_ref' THEN 'partner'
                                             ELSE 'invoice'
                                         END,
               invoice_reference_model  = 'be'
          FROM res_company c
         WHERE c.id = j.company_id
           AND invoice_reference_type = 'structured'
        """
    )

    util.remove_field(cr, "res.company", 'l10n_be_structured_comm')
    util.remove_field(cr, "res.config.settings", 'l10n_be_structured_comm')
    util.remove_view(cr, 'l10n_be_invoice_bba.res_config_settings_view_form')
