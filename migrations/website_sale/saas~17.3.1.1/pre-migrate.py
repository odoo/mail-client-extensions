import contextlib

from lxml import etree, html
from psycopg2.extras import Json

from odoo.upgrade import util


def migrate(cr, version):
    util.rename_field(cr, "product.product", "ribbon_id", "variant_ribbon_id")

    # set position of the ribbons
    util.create_column(cr, "product_ribbon", "position", "varchar", default="left")
    cr.execute(r"UPDATE product_ribbon SET position = 'right' WHERE html_class ~ '\yo_ribbon_right\y'")

    # set name of the ribbons
    util.create_column(cr, "product_ribbon", "name", "jsonb")
    cr.execute("SELECT id, html FROM product_ribbon")
    data = {id: {lang: extract_text(val) or "Ribbon" for lang, val in html.items()} for id, html in cr.fetchall()}
    cr.execute("UPDATE product_ribbon SET name = %s::jsonb->id::text", [Json(data)])

    util.remove_field(cr, "product.ribbon", "html")
    util.remove_field(cr, "product.ribbon", "html_class")


def extract_text(val):
    with contextlib.suppress(etree.ParserError):
        val = html.fromstring(val).text_content()
    return val
