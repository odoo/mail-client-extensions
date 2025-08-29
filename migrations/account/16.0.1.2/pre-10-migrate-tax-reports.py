import os

from odoo.upgrade import util

ODOO_MIG_16_MIGRATE_CUSTOM_TAX_REPORTS = util.str2bool(os.getenv("ODOO_MIG_16_MIGRATE_CUSTOM_TAX_REPORTS"), "")


def migrate(cr, version):
    # get ids of custom tax reports
    cr.execute(
        r"""
        SELECT atr.id, atr.name
          FROM account_tax_report atr
     LEFT JOIN ir_model_data imd
            ON imd.res_id = atr.id
           AND imd.model = 'account.tax.report'
           AND imd.module NOT LIKE '\_\_%'  -- __{export,import}__
         WHERE imd IS NULL
        """
    )

    custom_tax_reports = cr.fetchall()

    if not custom_tax_reports:
        pass
    elif not (ODOO_MIG_16_MIGRATE_CUSTOM_TAX_REPORTS or util.on_CI()):
        util.add_to_migration_reports(
            """
                <details>
                    <summary>
                        Due to a complete revamp of the reporting engine in Odoo 16, custom tax reports are not migrated by default.
                        The general suggestion is to try to fallback on the new capabilities of the standard reports, and recreate
                        your reports from scratch, if necessary.
                        However, if this would be too inconvenient, there is a possibility that opening a support ticket might help,
                        based on your specific case.
                        The custom tax reports that are being lost in this migration are the following ones:
                    </summary>
                    <ul>{}</ul>
                </details>
            """.format(" ".join(f"<li>{util.html_escape(name)} (id: {id:d})</li>" for id, name in custom_tax_reports)),
            category="Tax Reports",
            format="html",
        )
    else:
        util.ENVIRON["upgrade_custom_tax_report_ids_16"] = tuple(res[0] for res in custom_tax_reports)
