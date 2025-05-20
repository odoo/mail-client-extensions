from odoo.upgrade import util


def migrate(cr, version):
    util.update_record_from_xml(cr, "l10n_nl_reports.cron_l10n_nl_reports_status_process")
    cr.execute(
        """
        UPDATE ir_cron
           SET nextcall=now() at time zone 'UTC' + interval '12 hours'
         WHERE id=%s
        """,
        [util.ref(cr, "l10n_nl_reports.cron_l10n_nl_reports_status_process")],
    )
