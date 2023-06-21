# -*- coding: utf-8 -*-
import logging

from odoo import models

from odoo.addons.account.models import account_account  # noqa: F401

from odoo.upgrade import util

util.ENVIRON["upg_to_recompute"] = TO_RECOMPUTE = set()
_logger = logging.getLogger("l10n_mx.saas~16.2.2.0.post-migrate")


class AccountAccount(models.Model):
    _inherit = "account.account"
    _module = "l10n_mx"

    def write(self, vals):
        if self.env.context.get("_upgrade_l10n_mx_optim", False):
            # discard values that won't change to avoid trivial recomputes
            vals = {k: v for k, v in vals.items() if isinstance(self[k], models.Model) or v != self[k]}
            if "account_type" in vals:
                self.env.cr.execute("SELECT DISTINCT move_id FROM account_move_line WHERE account_id = %s", [self.id])
                _logger.info(
                    "account.move(%s) switched account_type from %r to %r, "
                    "always_tax_exigible will be recomputed on %s moves",
                    self.id,
                    self.account_type,
                    vals["account_type"],
                    self.env.cr.rowcount,
                )
                if self.env.cr.rowcount:
                    ids = [x for x, in self.env.cr.fetchall()]
                    TO_RECOMPUTE.update(ids)
                    AccountMove = self.env["account.move"]
                    with self.env.protecting(
                        [AccountMove._fields["always_tax_exigible"]], records=AccountMove.browse(ids)
                    ):
                        return super().write(vals)
        return super().write(vals)


def migrate(cr, version):
    pass
