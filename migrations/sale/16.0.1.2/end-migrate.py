from odoo.upgrade import util


def migrate(cr, version):
    if util.is_changed(cr, "sale.mail_template_sale_confirmation"):
        tid = util.ref(cr, "sale.mail_template_sale_confirmation")
        changes = [
            ("acquirer_id", "provider_id"),
            ("tx.provider", "tx.provider_code"),
            ("token_id.name", "token_id.display_name"),
        ]
        for old, new in changes:
            util.replace_in_all_jsonb_values(
                cr, "mail_template", "body_html", old, new, extra_filter=cr.mogrify("t.id = %s", [tid]).decode()
            )
    else:
        util.update_record_from_xml(cr, "sale.mail_template_sale_confirmation", ensure_references=True)
