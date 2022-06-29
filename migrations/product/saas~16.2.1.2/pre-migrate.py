from odoo.upgrade import util


def migrate(cr, version):
    util.force_noupdate(cr, "product.list0")
    util.replace_in_all_jsonb_values(cr, "mail_template", "body_html", "pricelist_id.currency_id", "currency_id")
