# -*- coding: utf-8 -*-
from odoo.upgrade import util


def migrate(cr, version):
    # Now an AbstractModel
    # HACK: rename `id` to allow removal with `remove_field` without removing the model itself
    util.rename_field(cr, "google.service", "id", "id_")
    cr.execute("SELECT name FROM ir_model_fields WHERE model = 'google.service'")
    for (field,) in cr.fetchall():
        util.remove_field(cr, "google.service", field)
    cr.execute("DROP TABLE google_service")
