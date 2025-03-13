from odoo.upgrade import util


def migrate(cr, version):
    util.rename_field(cr, "res.config.settings", "module_pos_viva_wallet", "module_pos_viva_com")

    util.create_column(cr, "pos_config", "currency_id", "integer")
    util.explode_execute(
        cr,
        """
         UPDATE pos_config AS c_up
           SET currency_id = CASE
                                 WHEN j.id IS NOT NULL THEN COALESCE(j.currency_id, com_j.currency_id)
                                 ELSE com_c.currency_id
                             END
          FROM pos_config AS c
          JOIN res_company AS com_c
            ON (c.company_id = com_c.id)
     LEFT JOIN account_journal AS j
            ON (c.journal_id = j.id)
     LEFT JOIN res_company AS com_j
            ON (j.company_id = com_j.id)
         WHERE c_up.id = c.id
        """,
        table="pos_config",
        alias="c_up",
    )

    util.remove_field(cr, "pos.config", "customer_display_type")
    util.remove_field(cr, "res.config.settings", "pos_customer_display_type")
