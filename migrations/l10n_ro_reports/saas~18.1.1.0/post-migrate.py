from odoo.upgrade import util


def migrate(cr, version):
    script = util.import_script("account_reports/saas~18.1.1.0/post-migrate.py")
    trial_balance_variants_xml_ids = [
        "l10n_ro_reports.l10n_ro_trial_balance_4_column",
        "l10n_ro_reports.l10n_ro_trial_balance_5_column",
    ]
    for trial_balance_variant in trial_balance_variants_xml_ids:
        script.migrate_report_annotations(cr, trial_balance_variant)
