from odoo.upgrade import util


def migrate(cr, version):
    if not util.version_gte("saas~18.5"):
        # Annnotations are moved to mail_messages in saas~18.5, to migrate those we only need the last part of the
        # line_id, here we add more to the line_id but nothing to the end so we don't need to do this beyond saas~18.4
        trial_balance_xml_id = "account_reports.trial_balance_report"
        migrate_report_annotations(cr, trial_balance_xml_id)


def migrate_report_annotations(cr, report_xml_id):
    env = util.env(cr)
    report = env.ref(report_xml_id, raise_if_not_found=False)
    if report and report.line_ids:
        report_line_id = report.line_ids[0].id

        cr.execute(
            """
            UPDATE account_report_annotation annotation
               SET line_id = CONCAT(
                    SPLIT_PART(line_id, '|', 1), -- Extract the part before the first '|'
                    '|~account.report.line~', %(report_line_id)s, '|{"groupby": "account_or_unaff_id"}',
                    SPLIT_PART(line_id, '|', 2) -- Extract the part after the first '|'
                )
             WHERE report_id = %(report_id)s
               AND line_id LIKE '~account.report~%%|~account.account~%%'
               AND ARRAY_LENGTH(STRING_TO_ARRAY(line_id, '|'), 1) = 2;
            """,
            {
                "report_id": report.id,
                "report_line_id": report_line_id,
            },
        )
