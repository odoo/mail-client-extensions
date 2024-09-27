from odoo.addons.base.maintenance.migrations import util


def migrate(cr, version):
    pass


if util.version_gte("saas~17.4"):
    from odoo import models

    from odoo.addons.data_cleaning.models import data_merge_rule  # noqa

    class DataMergeRule(models.Model):
        _name = "data_merge.rule"
        _inherit = ["data_merge.rule"]
        _module = "data_cleaning"
        _match_uniq = True
