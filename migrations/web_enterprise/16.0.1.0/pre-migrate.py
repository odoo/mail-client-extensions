from odoo.upgrade import util


def migrate(cr, version):
    cr.execute(
        "UPDATE ir_ui_view SET inherit_id = %s WHERE inherit_id = %s",
        [util.ref(cr, "web.webclient_bootstrap"), util.ref(cr, "web_enterprise.webclient_bootstrap")],
    )
    util.remove_view(cr, "web_enterprise.webclient_bootstrap")
