from odoo.upgrade import util


def migrate(cr, version):
    cr.execute(
        """
        UPDATE ir_ui_view
           SET customize_show = FALSE
         WHERE id = %s
        """,
        [util.ref(cr, "website_sale_slides.course_option_buy_course_now")],
    )
