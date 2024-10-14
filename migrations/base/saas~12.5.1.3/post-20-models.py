from ast import literal_eval

from odoo.addons.base.maintenance.migrations import util


def migrate(cr, version):
    IMFS = util.env(cr)["ir.model.fields.selection"]
    cr.execute(
        r"SELECT model, name, regexp_replace(selection, '^\s+|\s+$', '', 'g') FROM ir_model_fields WHERE state = 'manual'"
    )
    for model, name, selection in cr.fetchall():
        selection = literal_eval(selection or "[]")  # noqa: PLW2901
        IMFS._update_selection(model, name, selection)

    util.remove_column(cr, "ir_model_fields", "selection")
