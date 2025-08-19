from lxml import etree

from odoo.upgrade import util


def migrate(cr, version):
    cr.execute(
        """
        SELECT id
          FROM ir_ui_view
         WHERE key = 'website_sale.product_terms_and_conditions'
           AND website_id IS NOT NULL
        """
    )
    new_node = etree.fromstring("""
        <small class="text-muted mb-0">
            <a href="/terms" class="o_translate_inline text-muted"><u>Terms and Conditions</u></a><br/>
            30-day money-back guarantee<br/>
            Shipping: 2-3 Business Days
        </small>
    """)
    for vid in cr.fetchall():
        with util.edit_view(cr, view_id=vid) as arch:
            node = arch.find(""".//xpath[@expr="//div[@id='o_product_terms_and_share']"]""")
            if node is not None:
                node.addnext(new_node)
                node.getparent().remove(node)
            if arch.tag == "data":
                arch.tag = "t"
                arch.attrib["t-name"] = "website_sale.product_terms_and_conditions"
                arch.attrib.pop("inherit_id", None)
                arch.attrib.pop("customize_show", None)
