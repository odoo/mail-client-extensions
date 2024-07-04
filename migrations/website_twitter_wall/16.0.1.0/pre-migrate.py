from odoo.upgrade import util


def migrate(cr, version):
    cr.execute(
        """
        UPDATE ir_ui_view
           SET customize_show = FALSE
         WHERE id = %s
        """,
        [util.ref(cr, "website_twitter_wall.opt_twitter_wall_share")],
    )
