from odoo.upgrade import util


def migrate(cr, version):
    if not util.table_exists(cr, "account_tax_template"):
        # this script is also run for 16.0 database that have this module installed before the version bump[^1].
        # However, the `account.tax.template model is removed by the saas~16.2 account script[^2] that is run before this script.
        #
        # [^1]: https://github.com/odoo/odoo/commit/55a487ff2be8b1d976d07ea50f2332a82cb73f9c
        # [^2]: https://github.com/odoo/upgrade/blob/ac0b7445cbafa1e3c149aee40ce12fdddff91535/migrations/account/saas~16.2.1.2/pre-migrate.py#L62
        return  # nosemgrep: no-early-return

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
