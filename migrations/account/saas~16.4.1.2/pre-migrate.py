# -*- coding: utf-8 -*-

from odoo.upgrade import util


def migrate(cr, version):
    # Onboardings move
    util.remove_view(cr, "account.account_invoice_onboarding_panel")
    util.remove_view(cr, "account.account_invoice_onboarding_sale_tax_form")
    util.remove_view(cr, "account.onboarding_invoice_layout_step")
    util.remove_view(cr, "account.onboarding_create_invoice_step")
    util.remove_view(cr, "account.onboarding_bank_account_step")
    util.remove_view(cr, "account.onboarding_fiscal_year_step")
    util.remove_view(cr, "account.onboarding_chart_of_account_step")
    util.remove_view(cr, "account.onboarding_taxes_step")
    util.remove_view(cr, "account.account_dashboard_onboarding_panel")
    util.remove_view(cr, "account.onboarding_sale_tax_step")

    util.remove_record(cr, "account.action_open_account_onboarding_create_invoice")
    util.create_column(cr, "account_move", "incoterm_location", "varchar")

    if util.module_installed(cr, "l10n_sa"):
        util.move_field_to_module(cr, "account.move", "l10n_sa_delivery_date", "l10n_sa", "account")
        util.rename_field(cr, "account.move", "l10n_sa_delivery_date", "delivery_date")
        util.move_field_to_module(cr, "account.move", "l10n_sa_show_delivery_date", "l10n_sa", "account")
        util.rename_field(cr, "account.move", "l10n_sa_show_delivery_date", "show_delivery_date")
    else:
        util.create_column(cr, "account_move", "delivery_date", "date")

    cr.execute(
        """
        UPDATE res_company cc
           SET parent_id = NULL
          FROM res_company pc
         WHERE cc.parent_id = pc.id
           AND cc.chart_template IS NOT NULL
           AND cc.chart_template IS DISTINCT FROM pc.chart_template
     RETURNING cc.id,
               cc.name,
               cc.chart_template,
               pc.id,
               pc.name,
               pc.chart_template
        """
    )
    if cr.rowcount:
        util.add_to_migration_reports(
            category="Company Hierarchy",
            message="""
                <details>
                    <summary>
                        Companies now cannot have a chart of accounts different than the
                        one defined on the parent company. Therefore the parent company is removed
                        from the following:
                    </summary>
                    <ul>%s</ul>
                </details>"""
            % "".join(
                f"<li>{name} (id={id}) with chart '{coa}', had as parent company {p_name} (id={p_id}) with chart '{p_coa}'</li>"
                for id, name, coa, p_id, p_name, p_coa in cr.fetchall()
            ),
            format="html",
        )
