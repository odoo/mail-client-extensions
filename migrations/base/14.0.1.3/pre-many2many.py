from odoo.fields import Many2many

from odoo.addons.base.maintenance.migrations import util


def migrate(cr, version):

    original_update_db = Many2many.update_db
    fixed = set()

    def update_db(self, model, columns):
        comodel = model.env[self.comodel_name]
        if (
            self.relation not in fixed
            and util.table_exists(cr, self.relation)
            and len(util.get_columns(cr, self.relation, ignore=(self.column1, self.column2))) == 0
        ):
            fixed.add(self.relation)
            util.fixup_m2m(cr, self.relation, model._table, comodel._table, self.column1, self.column2)

        original_update_db(self, model, columns)

    Many2many.update_db = update_db
