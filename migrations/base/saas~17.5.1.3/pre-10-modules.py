from odoo.upgrade import util


def migrate(cr, version):
    util.remove_module(cr, "account_lock")

    util.merge_module(cr, "l10n_mx_edi_stock_extended_31", "l10n_mx_edi_stock_extended")
    util.force_upgrade_of_fresh_module(cr, "html_editor", init=False)
    if util.module_installed(cr, "mrp_account") and not util.module_installed(cr, "project"):
        # The following query identifies whether there is at least a BOM or a MO that has an analytic distribution
        # which contains exactly one line at 100%. If that's the case, we force the installation of the project module
        # because we will create for each BOM and MO that meets this condition, a project that has the same analytic
        # accounts as the ones from their analytic distribution, in order to preserve user data
        cr.execute("""
           (SELECT 1
              FROM mrp_production,
                   JSONB_EACH_TEXT(analytic_distribution)
          GROUP BY id
            HAVING COUNT(*) = 1
               AND SUM(value::numeric) = 100
             LIMIT 1)
             UNION
             (WITH _mrp_bom AS (
                   SELECT CAST(SPLIT_PART(res_id, ',', 2) AS INTEGER) AS id,
                          CAST(value_text AS jsonb) AS analytic_distribution
                     FROM ir_property
                    WHERE name = 'analytic_distribution_text'
                      AND value_text != 'false'
                 )
            SELECT 1
              FROM _mrp_bom,
                   JSONB_EACH_TEXT(analytic_distribution)
          GROUP BY id
            HAVING COUNT(*) = 1
               AND SUM(value::numeric) = 100.0
             LIMIT 1)
        """)
        if cr.rowcount:
            util.add_to_migration_reports(
                "We introduced a new feature allowing projects to have multiple analytic accounts (one per plan). "
                "We then removed the analytic distribution of Manufacturing Orders and Bills of Materials "
                "and replaced it with a project field, whose analytic accounts represent the analytic distribution. "
                "For MOs and BOMs that had an analytic distribution containing exactly one line at 100%, new projects "
                "were created and linked to them. Each project will contain the same analytic accounts as in the "
                "analytic distribution of the MO/BOM to preserve user data.",
                "Manufacturing/Project/Analytic",
            )
            util.force_install_module(cr, "project_mrp")
            util.force_upgrade_of_fresh_module(cr, "project_mrp")
