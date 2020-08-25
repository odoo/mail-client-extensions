# -*- coding: utf-8 -*-
from odoo.upgrade import util
from odoo.tools.mail import html_sanitize


def migrate(cr, version):
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
