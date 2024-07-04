from odoo.upgrade import util


def migrate(cr, version):
    cr.execute(
        """
        UPDATE ir_ui_view
           SET customize_show = FALSE
         WHERE id IN %s
        """,
        [
            (
                util.ref(cr, "website_helpdesk.navbar_search_date"),
                util.ref(cr, "website_helpdesk.navbar_search_type"),
                util.ref(cr, "website_helpdesk.navbar_search_tag"),
            )
        ],
    )
