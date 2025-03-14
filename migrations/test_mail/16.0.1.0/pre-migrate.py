from odoo.upgrade import util


def migrate(cr, version):
    util.rename_field(cr, "mail.test.track.selection", "type", "selection_type")

    # Remove fields from mixin
    util.remove_field(cr, "mail.test.composer.mixin", "model_object_field")
    util.remove_field(cr, "mail.test.composer.mixin", "sub_object")
    util.remove_field(cr, "mail.test.composer.mixin", "sub_model_object_field")
    util.remove_field(cr, "mail.test.composer.mixin", "null_value")
    util.remove_field(cr, "mail.test.composer.mixin", "copyvalue")
