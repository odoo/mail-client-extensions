from odoo.upgrade import util


def migrate(cr, version):
    fr = util.ref(cr, "base.fr")

    cr.execute(
        """
        UPDATE account_tax_template AS tt
           SET tax_group_id = NULL
          FROM account_tax_group AS tg,
               account_chart_template AS ct
         WHERE tt.tax_group_id = tg.id
           AND tt.chart_template_id = ct.id
           AND ct.id = %s
           AND ct.country_id = %s
           AND tg.country_id != %s
        """,
        [util.ref(cr, "l10n_fr.l10n_fr_pcg_chart_template"), fr, fr],
    )

    cr.execute(
        """
        DELETE FROM ir_model_data AS md
         USING account_tax_group AS tg
         WHERE md.module = 'l10n_fr'
           AND md.model = 'account.tax.group'
           AND md.res_id = tg.id
           AND tg.country_id != %s
        """,
        [fr],
    )
