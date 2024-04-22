from odoo import models

from odoo.addons.account_edi.models import account_journal  # noqa

from odoo.upgrade import util


def migrate(cr, version):
    pass


class AccountJournal(models.Model):
    _inherit = "account.journal"
    _module = "account_edi"

    def _compute_edi_format_ids(self):
        if self.env.context.get("_upg_iter_browse"):
            return super()._compute_edi_format_ids()
        util.iter_browse(
            self.env["account.journal"].with_context(_upg_iter_browse=True, tracking_disable=True), self.ids
        )._compute_edi_format_ids()
        return True
