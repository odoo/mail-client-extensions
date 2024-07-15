from odoo.upgrade import util


def migrate(cr, version):
    for fname in ["local_url", "image_src", "image_width", "image_height", "original_id"]:
        util.move_field_to_module(cr, "ir.attachment", fname, "web_editor", "html_editor")
