from odoo.upgrade import util


def migrate(cr, version):
    # We need the own checks payment method instead of the old check_printing
    util.update_record_from_xml(cr, "l10n_latam_check.account_payment_method_own_checks")

    # Update payment method lines on the journal
    cr.execute(
        """
        UPDATE account_payment_method_line apml
           SET payment_method_id = %s
          FROM account_journal aj, account_payment_method apm
         WHERE aj.l10n_latam_manual_checks
           AND apml.journal_id = aj.id
           AND apml.payment_method_id = apm.id
           AND apm.code='check_printing'
    """,
        [util.ref(cr, "l10n_latam_check.account_payment_method_own_checks")],
    )

    # Create l10n_latam_check table already, so we can do most of the work in pre
    cr.execute(
        """
        CREATE TABLE l10n_latam_check (
            id SERIAL PRIMARY KEY,
            create_uid integer,
            create_date timestamp without time zone,
            write_uid integer,
            write_date timestamp without time zone,
            company_id integer,
            payment_id integer,
            name varchar,
            current_journal_id integer,
            payment_date date,
            amount float8,
            payment_method_line_id integer,
            outstanding_line_id integer,
            issuer_vat varchar,
            bank_id integer
        )
    """
    )

    # Migrate own checks from payments to the separate table
    # The liquidity_line points to itself, but if a payment is done with multiple checks, it will point to a separate journal entry
    payment_field = "payment_id"
    if util.version_gte("saas~17.5"):
        payment_field = "origin_payment_id"
    query = util.format_query(
        cr,
        """
        INSERT INTO l10n_latam_check
                   (company_id, payment_id, name,
                    current_journal_id,
                    payment_date,
                    amount, payment_method_line_id, outstanding_line_id)
             SELECT ap.company_id, ap.id, ap.check_number,
                    ap.l10n_latam_check_current_journal_id,
                    ap.l10n_latam_check_payment_date,
                    ap.amount, ap.payment_method_line_id, aml.id
               FROM account_payment ap
               JOIN account_payment_method_line apml
                 ON ap.payment_method_line_id = apml.id
               JOIN account_payment_method apm
                 ON apml.payment_method_id = apm.id
               JOIN account_move am
                 ON am.{} = ap.id
               JOIN account_move_line aml
                 ON aml.move_id = am.id
               JOIN account_account account
                 ON aml.account_id = account.id
              WHERE ABS(aml.amount_currency) = ap.amount
                AND account.account_type NOT IN ('asset_receivable', 'liability_payable')
                AND apm.code = 'own_checks'
           ORDER BY aml.id
        """,
        payment_field,
    )
    cr.execute(query)

    # Migrate new 3rd party checks from payments to the separate table
    cr.execute(
        """
        INSERT INTO l10n_latam_check(
                    company_id, payment_id, name,
                    current_journal_id, payment_date,
                    amount, payment_method_line_id,
                    issuer_vat, bank_id)
             SELECT ap.company_id, ap.id, ap.check_number,
                    ap.l10n_latam_check_current_journal_id,
                    ap.l10n_latam_check_payment_date,
                    ap.amount, ap. payment_method_line_id,
                    ap.l10n_latam_check_issuer_vat,
                    ap.l10n_latam_check_bank_id
               FROM account_payment ap
               JOIN account_payment_method_line apml
                 ON ap.payment_method_line_id = apml.id
               JOIN account_payment_method apm
                 ON apml.payment_method_id = apm.id
              WHERE apm.code = 'new_third_party_checks'
    """
    )

    cr.execute(
        """
        WITH checks AS (
            SELECT id,
                   ROW_NUMBER() OVER (PARTITION BY name, payment_method_line_id ORDER BY id) AS rn
              FROM l10n_latam_check
             WHERE outstanding_line_id IS NOT NULL
        )
        UPDATE l10n_latam_check llc
           SET name = llc.name || ' - #' || checks.rn
          FROM checks
         WHERE llc.id = checks.id
           AND checks.rn > 1
        """
    )
    # Create new link table from the moving of 3rd party checks
    util.create_m2m(
        cr, "l10n_latam_check_account_payment_rel", "l10n_latam_check", "account_payment", "check_id", "payment_id"
    )

    # Link move of 3rd party checks
    cr.execute(
        """
        INSERT INTO l10n_latam_check_account_payment_rel (check_id, payment_id)
             SELECT lc.id, ap.id
               FROM account_payment ap
               JOIN account_payment ap_check
                 ON ap.l10n_latam_check_id = ap_check.id
               JOIN l10n_latam_check lc
                 ON lc.payment_id = ap_check.id
    """
    )

    util.remove_view(cr, "l10n_latam_check.view_account_journal_tree")
    util.remove_view(cr, "l10n_latam_check.view_account_own_check_tree")

    util.remove_field(cr, "account.payment.register", "l10n_latam_check_payment_date")

    util.remove_field(cr, "account.payment.register", "l10n_latam_manual_checks")
    util.remove_field(cr, "account.payment.register", "l10n_latam_check_issuer_vat")
    util.remove_field(cr, "account.payment.register", "l10n_latam_check_bank_id")
    util.remove_field(cr, "account.payment.register", "l10n_latam_check_id")
    util.remove_field(cr, "account.payment.register", "l10n_latam_check_number")

    util.remove_field(cr, "account.payment", "l10n_latam_manual_checks")
    util.remove_field(cr, "account.payment", "l10n_latam_check_payment_date")
    util.remove_field(cr, "account.payment", "l10n_latam_check_current_journal_id")
    util.remove_field(cr, "account.payment", "l10n_latam_check_issuer_vat")
    util.remove_field(cr, "account.payment", "l10n_latam_check_bank_id")
    util.remove_field(cr, "account.payment", "l10n_latam_check_number")
    util.remove_field(cr, "account.payment", "l10n_latam_check_operation_ids")
    util.remove_field(cr, "account.payment", "l10n_latam_check_id")
    util.remove_field(cr, "account.payment", "l10n_latam_check_warning_msg")

    util.remove_field(cr, "account.journal", "l10n_latam_manual_checks")
