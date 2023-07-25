# -*- coding: utf-8 -*-

from odoo.upgrade import util


def migrate(cr, version):
    util.create_column(cr, "res_company", "account_peppol_migration_key", "varchar")
    cr.execute(
        r"""
        WITH deleted_params AS (
            DELETE FROM ir_config_parameter p
                  USING res_company c
                  WHERE key = CONCAT('account_peppol.migration_key_', c.id)
              RETURNING c.id AS id,
                        p.value AS migration_key
        )
        UPDATE res_company AS company
           SET account_peppol_migration_key = deleted_params.migration_key
          FROM deleted_params
         WHERE company.id = deleted_params.id
        """
    )

    util.remove_field(cr, "account_edi_proxy_client.user", "peppol_migration_key")
    util.remove_field(cr, "res.company", "account_peppol_attachment_ids")
    util.remove_field(cr, "res.config.settings", "account_peppol_attachment_ids")
    util.remove_field(cr, "account.move.send", "peppol_proxy_state")
