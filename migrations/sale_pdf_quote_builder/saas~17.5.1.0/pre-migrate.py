from odoo.upgrade import util


def migrate(cr, version):
    cr.execute(
        """
        CREATE TABLE sale_pdf_form_field (
            id SERIAL NOT NULL PRIMARY KEY
        )
    """
    )
    cr.execute(
        """
        CREATE TABLE quotation_document (
            id SERIAL NOT NULL PRIMARY KEY
        )
    """
    )
    util.create_m2m(
        cr,
        "product_document_sale_pdf_form_field_rel",
        "product_document",
        "sale_pdf_form_field",
    )
    util.create_m2m(
        cr,
        "quotation_document_sale_pdf_form_field_rel",
        "quotation_document",
        "sale_pdf_form_field",
    )
    util.create_m2m(
        cr,
        "quotation_document_sale_order_rel",
        "sale_order",
        "quotation_document",
    )
    util.create_m2m(
        cr,
        "sale_order_line_product_document_rel",
        "sale_order_line",
        "product_document",
    )
