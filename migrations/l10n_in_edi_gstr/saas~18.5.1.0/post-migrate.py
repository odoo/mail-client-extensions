from odoo.upgrade import util


def migrate(cr, version):
    gstr1_return_type = util.ref(cr, "l10n_in_reports.in_gstr1_return_type")

    # Update only GSTR1 returns
    cr.execute(
        """
        UPDATE account_return ar
           SET l10n_in_gstr1_include_einvoice = rel.gstr1_include_einvoice
          FROM l10n_in_gst_return_period rel
         WHERE ar.v19_l10n_in_return_period_id = rel.id
           AND ar.type_id = %s
           AND rel.gstr1_include_einvoice IS NOT NULL
        """,
        (gstr1_return_type,),
    )
