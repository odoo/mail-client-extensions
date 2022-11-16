from odoo.upgrade import util


def migrate(cr, version):
    cr.execute(
        """
        SELECT m.model, f.name
        FROM ir_model_fields f
        INNER JOIN ir_model m ON f.model_id = m.id
        WHERE f.name = '__last_update';
        """
    )
    for (model, field) in cr.fetchall():
        util.remove_field(cr, model, field, skip_inherit="*")
