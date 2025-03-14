from odoo.upgrade import util


def migrate(cr, version):
    cr.execute(
        "UPDATE slide_channel SET share_channel_template_id = %s WHERE share_channel_template_id IS NULL",
        [util.ref(cr, "website_slides.mail_template_channel_shared")],
    )
