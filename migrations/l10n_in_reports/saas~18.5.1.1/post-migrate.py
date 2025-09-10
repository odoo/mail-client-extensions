from odoo.upgrade import util


def migrate(cr, version):
    util.explode_execute(
        cr,
        """
        UPDATE l10n_in_gst_return_period
           SET return_period_month_year = TO_CHAR(end_date::timestamp without time zone, 'MMYYYY')
        """,
        table="l10n_in_gst_return_period",
    )
    gstr1_return_type = util.ref(cr, "l10n_in_reports.in_gstr1_return_type")
    gstr2b_return_type = util.ref(cr, "l10n_in_reports.in_gstr2b_return_type")

    # Create a temporary column to store the reference between old l10n_in.gst.return.period and account.return
    util.create_column(cr, "account_return", "v19_l10n_in_return_period_id", "integer")

    # Create the two records for account return, insert data from l10n_in_gst_return_period to account_return
    # Seperate the GSTR-1 and GSTR-2B returns

    cr.execute(
        """
        INSERT INTO account_return(
                    v19_l10n_in_return_period_id, active,
                    create_uid, write_uid, create_date, write_date,
                    company_id, tax_unit_id,
                    l10n_in_gstr_reference,
                    l10n_in_gstr1_blocking_level,
                    date_from, date_to,
                    type_id, audit_status,
                    l10n_in_month_year,
                    date_deadline,
                    is_completed,
                    name,
                    state,
                    l10n_in_gstr1_status
                    )
             SELECT id, True,
                    create_uid, write_uid, create_date, write_date,
                    company_id, tax_unit_id,
                    gstr_reference,
                    gstr1_blocking_level,
                    start_date AS date_from, end_date AS date_to,
                    %s AS type_id, 'ongoing' AS audit_status,
                    COALESCE(return_period_month_year, TO_CHAR(end_date, 'MMYYYY')) AS l10n_in_month_year,
                    end_date + INTERVAL '7 days' As date_deadline,
                    CASE
                        WHEN gstr1_status = 'filed' THEN True
                        ELSE False
                     END AS is_completed,
                    jsonb_set(
                        '{}'::jsonb,
                        '{en_US}',
                        to_jsonb(
                            CASE
                                WHEN periodicity = 'monthly'
                                THEN 'GSTR-1 ' || TRIM(TO_CHAR(start_date, 'FMMonth YYYY')) || ' '
                                WHEN periodicity = 'quarter'
                                THEN 'GSTR-1 Q ' || (TO_CHAR(start_date, 'Q YYYY')) || ' '
                                ELSE
                                    'GSTR- ' || COALESCE(return_period_month_year, 'new')
                            END
                        )
                    ) AS name,
                    CASE
                        WHEN gstr1_status = 'to_send' THEN 'new'
                        WHEN gstr1_status = 'sending' AND gstr1_blocking_level IN ('error', 'warning') THEN 'sending_error'
                        WHEN gstr1_status = 'sending' THEN 'sending'
                        WHEN gstr1_status = 'waiting_for_status' THEN 'waiting_for_status'
                        WHEN gstr1_status = 'error_in_invoice' THEN 'error_in_invoice'
                        WHEN gstr1_status = 'sent' THEN 'sent'
                        WHEN gstr1_status = 'filed' THEN 'filed'
                        ELSE 'new'
                     END AS state,
                    CASE
                        WHEN gstr1_status = 'to_send' THEN 'new'
                        WHEN gstr1_status = 'sending' AND gstr1_blocking_level IN ('error', 'warning') THEN 'sending_error'
                        WHEN gstr1_status = 'sending' THEN 'sending'
                        WHEN gstr1_status = 'waiting_for_status' THEN 'waiting_for_status'
                        WHEN gstr1_status = 'error_in_invoice' THEN 'error_in_invoice'
                        WHEN gstr1_status = 'sent' THEN 'sent'
                        WHEN gstr1_status = 'filed' THEN 'filed'
                        ELSE 'new'
                     END AS l10n_in_gstr1_status
               FROM l10n_in_gst_return_period
        """,
        (gstr1_return_type,),
    )

    cr.execute(
        """
        INSERT INTO account_return (
                    v19_l10n_in_return_period_id, active,
                    create_uid, write_uid, create_date, write_date,
                    company_id, tax_unit_id,
                    l10n_in_irn_status,
                    l10n_in_gstr2b_blocking_level,
                    date_from, date_to,
                    type_id, audit_status,
                    l10n_in_month_year,
                    date_deadline,
                    l10n_in_irn_fetch_date,
                    is_completed,
                    name,
                    state,
                    l10n_in_gstr2b_status
                    )
             SELECT id, True,
                    create_uid, write_uid, create_date, write_date,
                    company_id, tax_unit_id,
                    irn_status,
                    gstr2b_blocking_level,
                    start_date AS date_from, end_date AS date_to,
                    %s AS type_id, 'ongoing' AS audit_status,
                    COALESCE(return_period_month_year, TO_CHAR(end_date, 'MMYYYY')) AS l10n_in_month_year,
                    end_date + INTERVAL '14 days' AS date_deadline,
                    end_date + INTERVAL '2 days' AS l10n_in_irn_fetch_date,
                    CASE
                        WHEN gstr2b_status IN ('partially_matched', 'fully_matched') THEN True
                        ELSE False
                     END AS is_completed,
                    jsonb_set(
                        '{}'::jsonb,
                        '{en_US}',
                        to_jsonb(
                            CASE
                                WHEN periodicity = 'monthly'
                                THEN 'GSTR-2B ' || TRIM(TO_CHAR(start_date, 'FMMonth YYYY')) || ' '
                                WHEN periodicity = 'quarter'
                                THEN 'GSTR-2B Q ' || (TO_CHAR(start_date, 'Q YYYY')) || ' '
                                ELSE
                                    'GSTR- ' || COALESCE(return_period_month_year, 'new')
                            END
                        )
                    ) AS name,
                    CASE
                        WHEN gstr2b_status = 'not_received' THEN 'new'
                        WHEN gstr2b_status = 'waiting_reception' AND gstr2b_blocking_level IN ('error', 'warning') THEN 'error_in_fetching'
                        WHEN gstr2b_status = 'waiting_reception' THEN 'fetching'
                        WHEN gstr2b_status = 'being_processed' AND gstr2b_blocking_level IN ('error', 'warning') THEN 'error_in_fetching'
                        WHEN gstr2b_status = 'being_processed' THEN 'fetch'
                        WHEN gstr2b_status = 'partially_matched' THEN 'partially_matched'
                        WHEN gstr2b_status = 'fully_matched' THEN 'matched'
                        ELSE 'new'
                     END AS state,
                    CASE
                        WHEN gstr2b_status = 'not_received' THEN 'new'
                        WHEN gstr2b_status = 'waiting_reception' AND gstr2b_blocking_level IN ('error', 'warning') THEN 'error_in_fetching'
                        WHEN gstr2b_status = 'waiting_reception' THEN 'fetching'
                        WHEN gstr2b_status = 'being_processed' AND gstr2b_blocking_level IN ('error', 'warning') THEN 'error_in_fetching'
                        WHEN gstr2b_status = 'being_processed' THEN 'fetch'
                        WHEN gstr2b_status = 'partially_matched' THEN 'partially_matched'
                        WHEN gstr2b_status = 'fully_matched' THEN 'matched'
                        ELSE 'new'
                     END AS l10n_in_gstr2b_status
               FROM l10n_in_gst_return_period
        """,
        (gstr2b_return_type,),
    )

    # If there are errors in l10n_in_gst_return_period records then insert them
    # into chatter of newly created account returns
    root_partner = util.ref(cr, "base.partner_root")
    cr.execute(
        """
        INSERT INTO mail_message (
                    model, res_id, body,
                    message_type, author_id
                    )
             SELECT 'account.return', ar.id,
                    'Migrated GSTR1 Error: ' || rel.gstr1_error,
                    'comment',
                    %s
               FROM account_return ar
               JOIN l10n_in_gst_return_period rel
                 ON ar.v19_l10n_in_return_period_id = rel.id
              WHERE ar.type_id = %s
                AND rel.gstr1_error IS NOT NULL
                AND rel.gstr1_error != ''
        """,
        (root_partner, gstr1_return_type),
    )
    cr.execute(
        """
        INSERT INTO mail_message (
                    model, res_id, body,
                    message_type, author_id
                    )
             SELECT 'account.return', ar.id,
                    'Migrated GSTR2B Error: ' || rel.gstr2b_error,
                    'comment', %s
               FROM account_return ar
               JOIN l10n_in_gst_return_period rel
                 ON ar.v19_l10n_in_return_period_id = rel.id
              WHERE ar.type_id = %s
                AND rel.gstr2b_error IS NOT NULL
                AND rel.gstr2b_error != ''
        """,
        (root_partner, gstr2b_return_type),
    )

    cr.execute(
        """
        INSERT INTO account_return_res_company_rel (account_return_id, res_company_id)
             SELECT return.id, COALESCE(tax_unit_company_rel.res_company_id, company.id)
               FROM account_return return
               LEFT JOIN account_tax_unit_res_company_rel tax_unit_company_rel
                 ON tax_unit_company_rel.account_tax_unit_id = return.tax_unit_id
               JOIN res_company company
                 ON company.id = return.company_id
               JOIN res_country country
                 ON country.id = company.account_fiscal_country_id
              WHERE country.code = 'IN'
                 ON CONFLICT DO NOTHING
        """
    )
    # Insert into new m2m field for l10n_in_gstr2b_json_ids field from
    # the m2m field gstr2b_json_from_portal_ids and ir_attachment_l10n_in_gst_return_period_rel table
    cr.execute(
        """
        INSERT INTO account_return_gstr2b_json_rel (account_return_id, ir_attachment_id)
             SELECT ar.id, rel.ir_attachment_id
               FROM account_return ar
               JOIN ir_attachment_l10n_in_gst_return_period_rel rel
                 ON rel.l10n_in_gst_return_period_id = ar.v19_l10n_in_return_period_id
              WHERE ar.type_id = %s
        """,
        (gstr2b_return_type,),
    )

    # Insert into new m2m table for field l10n_in_irn_json_attachment_ids from
    # the m2m field list_of_irn_json_attachment_ids and irn_attachment_portal_json table
    cr.execute(
        """
        INSERT INTO irn_attachment_portal_account_return_json (account_return_id, ir_attachment_id)
             SELECT ar.id, rel.ir_attachment_id
               FROM account_return ar
               JOIN irn_attachment_portal_json rel
                 ON rel.l10n_in_gst_return_period_id = ar.v19_l10n_in_return_period_id
              WHERE ar.type_id = %s
        """,
        (gstr2b_return_type,),
    )

    # Update the l10n_in_account_return_id field in account move model for corresponding l10n_in_gst_return_period
    util.explode_execute(
        cr,
        cr.mogrify(
            """
            UPDATE account_move am
               SET l10n_in_account_return_id = ar.id
              FROM account_return ar
             WHERE ar.v19_l10n_in_return_period_id = am.l10n_in_gst_return_period_id
               AND ar.type_id = %s
            """,
            (gstr2b_return_type,),
        ).decode(),
        table="account_move",
        alias="am",
    )

    cr.execute(
        """
        UPDATE l10n_in_gstr_document_summary_line dsl
           SET return_period_id = ar.id
          FROM account_return ar
         WHERE dsl.return_period_id = ar.v19_l10n_in_return_period_id
           AND ar.type_id = %s
        """,
        (gstr1_return_type,),
    )

    # migrate attachments to gstr1 returns
    cr.execute(
        """
        UPDATE ir_attachment a
           SET res_model = 'account.return',
               res_id = ar.id
          FROM account_return ar
          WHERE a.res_model = 'l10n_in.gst.return.period'
            AND a.res_id = ar.v19_l10n_in_return_period_id
            AND ar.type_id = %s
        """,
        (gstr1_return_type,),
    )

    # migrate the mail followers to gstr1 returns
    cr.execute(
        """
        UPDATE mail_followers f
           SET res_model = 'account.return',
               res_id = ar.id
          FROM account_return ar
         WHERE f.res_model = 'l10n_in.gst.return.period'
           AND f.res_id = ar.v19_l10n_in_return_period_id
           AND ar.type_id = %s
        """,
        (gstr1_return_type,),
    )

    # migrate the scheduled activites to gstr1 returns
    model_account_return = util.ref(cr, "account_reports.model_account_return")
    cr.execute(
        """
        UPDATE mail_activity a
           SET res_model = 'account.return',
               res_model_id = %s,
               res_id = ar.id,
               res_name = ar.name->>'en_US'
          FROM account_return ar
         WHERE a.res_model = 'l10n_in.gst.return.period'
           AND a.res_id = ar.v19_l10n_in_return_period_id
           AND ar.type_id = %s
        """,
        (model_account_return, gstr1_return_type),
    )

    # migrate all the chatter messages to gstr1 returns
    cr.execute(
        """
        UPDATE mail_message mm
           SET model = 'account.return',
               res_id = ar.id
          FROM account_return ar
         WHERE mm.model = 'l10n_in.gst.return.period'
           AND mm.res_id = ar.v19_l10n_in_return_period_id
           AND ar.type_id = %s;
        """,
        (gstr1_return_type,),
    )

    # Remove the old l10n_in.gst.return.period model and its fields
    util.remove_field(cr, "account.move", "l10n_in_gst_return_period_id")
    util.add_to_migration_reports(
        """
            <details>
                <summary>
                    Migration of GST Return Period.
                    GST Return Period records are converted to Account Returns.
                    <br>
                    <strong>Note:</strong>Now the tax returns for GSTR-1 and GSTR-2B will be created separately.
                    <br>
                    <strong>All the Chatter details from previous records are now shown under GSTR-1 Tax returns</strong>
                </summary>
            </details>
        """
        "l10n_in_reports",
        format="html",
    )
