# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util


def migrate(cr, version):
    cr.execute('ALTER TABLE "res_lang" DROP CONSTRAINT "res_lang_code_uniq" CASCADE')

    util.rename_field(cr, "ir.model.fields", "copy", "copied")

    util.create_column(cr, "ir_attachment", "res_model_name", "varchar")
    util.create_column(cr, "ir_attachment", "active", "boolean")
    cr.execute(
        """
        UPDATE ir_attachment a
           SET res_model_name = m.name
          FROM ir_model m
         WHERE m.model = a.res_model
           AND a.res_model_name IS NULL
    """
    )
    cr.execute("UPDATE ir_attachment SET active=true WHERE active IS NULL")

    util.create_column(cr, "ir_module_module", "to_buy", "boolean")
    cr.execute("UPDATE ir_module_module SET to_buy=false")

    util.create_column(cr, "res_company", "base_onboarding_company_state", "varchar")
    cr.execute(
        """
        UPDATE res_company c
           SET base_onboarding_company_state = CASE WHEN p.street IS NOT NULL THEN 'just_done'
                                                    ELSE 'not_done'
                                                END
          FROM res_partner p
         -- code actually use 'contact' sub partner, but direct partner is a pretty good approximation
         WHERE p.id = c.partner_id
    """
    )

    util.create_column(cr, "res_company", "external_report_layout_id", "int4")
    cr.execute(
        r"""
        WITH layouts AS (
            SELECT substring(name, 17) AS name,
                   res_id AS id
              FROM ir_model_data
             WHERE model = 'ir.ui.view'
               AND module = 'web'
               AND name LIKE 'external\_layout\_%'
        )
        UPDATE res_company c
           SET external_report_layout_id = l.id
          FROM layouts l
         WHERE l.name = c.external_report_layout
    """
    )
    util.remove_field(cr, "res.company", "external_report_layout")
