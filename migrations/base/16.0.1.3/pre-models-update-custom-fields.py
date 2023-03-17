from odoo import fields, models

orig_update_db = fields.One2many.update_db


def ignore_manual(self, model, columns):
    if self.manual:
        # for manual one2many we always skip update_db since it only checks the comodel
        # which may not be loaded yet
        return
    return orig_update_db(self, model, columns)


fields.One2many.update_db = ignore_manual


def migrate(cr, version):
    pass


class Base(models.AbstractModel):
    _inherit = "base"
    _module = "base"

    def _auto_init(self):
        super(Base, self.with_context(update_custom_fields=True))._auto_init()
