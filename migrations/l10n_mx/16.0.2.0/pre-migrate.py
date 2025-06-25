from odoo import models

from odoo.addons.account.models import account_account  # noqa: F401

from odoo.addons.base.maintenance.migrations import util


class AccountGroup(models.Model):
    _inherit = "account.group"
    _module = "l10n_mx"
    _match_uniq = True
    _match_uniq_warning = (
        'The account group "{name}" from Mexican localization (l10n_mx) was linked to '
        'an existing group (id={id}) since it has same code prefix "{code_prefix_start}"'
    )


def migrate(cr, version):
    # Don't drop the column to use it in post
    util.remove_field(cr, "account.account.tag", "nature", drop_column=False)
    cr.execute(
        """
        CREATE UNIQUE INDEX _upg_mx_account_groups
            ON account_group(company_id, code_prefix_start, code_prefix_end)
        """
    )
