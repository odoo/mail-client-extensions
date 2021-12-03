# -*- coding: utf-8 -*-
from odoo.upgrade import util
from odoo.tools.mail import html_sanitize
import re


def migrate(cr, version):
    # ==========================================================================
    # Task 2304199 : html field for terms & conditions
    # ==========================================================================

    util.create_column(cr, "res_company", "terms_type", "varchar")
    util.create_column(cr, "res_company", "invoice_terms_html", "text")
    html_content = """<h1 style="text-align: center; ">Terms &amp; Conditions</h1><p>Your conditions...</p>"""
    term_type = "plain"
    # We only reuse the website_sale.terms template if it has been modified. Default values is not kept.
    if util.module_installed(cr, "website_sale"):
        cr.execute(
            """
             SELECT arch_db
               FROM ir_ui_view
              WHERE key = 'website_sale.terms'
                AND arch_updated = true
                AND arch_db IS NOT NULL
            """
        )
        if cr.rowcount:
            if cr.rowcount > 1:
                util.add_to_migration_reports(
                    "Upgrade of multiple Terms & Conditions templates is not supported.", "eCommerce"
                )
            else:
                term_type = "html"
                template_content = cr.fetchone()[0]
                html_content = html_sanitize(template_content, sanitize_attributes=True)
                ICP = util.env(cr)["ir.config_parameter"]
                ICP.set_param("account.use_invoice_terms", True)
    cr.execute("UPDATE res_company SET terms_type = %s, invoice_terms_html = %s ", [term_type, html_content])

    # ==========================================================================
    # Task 2346404 : Journals short codes unicity
    # ==========================================================================

    cr.execute("""
        SELECT TRIM(code), company_id, ARRAY_AGG(id ORDER BY id)
        FROM account_journal
        GROUP BY TRIM(code), company_id
        HAVING count(*) > 1
    """)
    multi_code_data = cr.fetchall()
    for code, company_id, journal_ids in multi_code_data:
        # This use case is really rare; the content of this loop should nearly never be executed.
        cr.execute("""
            SELECT DISTINCT TRIM(code)
            FROM account_journal
            WHERE company_id = %s
        """, (company_id,))

        all_journal_codes = {elem[0] for elem in cr.fetchall()}

        # The first journal found keeps its original code; we rename the other ones
        for to_fix_id in journal_ids[1:]:

            # Find a new unused code for this journal
            new_code = code
            # Remove all digits from the end
            code_prefix = re.sub(r'\d+$', '', code.strip())
            if not code_prefix:
                # the whole code was a number :/
                code_prefix = code.strip() + 'N'
            counter = 0
            while counter <= len(all_journal_codes) and new_code in all_journal_codes:
                counter += 1
                counter_str = str(counter)
                copy_prefix = code_prefix[:5 - len(counter_str)]  # 5 is the max size of journal code field
                new_code = ("%s%s" % (copy_prefix, counter_str))

            if counter > len(all_journal_codes):
                raise util.MigrationError(
                    f"Could not create a new short code automatically for journal with id {to_fix_id} (code={code})."
                )
            else:
                all_journal_codes.add(new_code)
                cr.execute("""
                    UPDATE account_journal
                    SET code = %s
                    WHERE id = %s
                """, (new_code, to_fix_id))

    if multi_code_data:
        util.add_to_migration_reports(
            "Some journals were using the same short codes. Since this is not "
            "allowed anymore, a unique short code has been computed for them. "
            "The sequences of their entries stay unchanged, you can change "
            "them manually if you wish to.", "Accounting")

    # ==========================================================================
    # Task 2116063 : Rewrite online synchronization for Odoo Finance
    # ==========================================================================

    util.remove_field(cr, 'res.config.settings', 'module_account_yodlee')
    util.remove_field(cr, 'res.config.settings', 'module_account_plaid')

    # ==========================================================================
    # Task 2363287 : Avoid tax tags inversion on aml
    # ==========================================================================
    util.create_column(cr, 'account_move_line', 'tax_tag_invert', 'bool')
