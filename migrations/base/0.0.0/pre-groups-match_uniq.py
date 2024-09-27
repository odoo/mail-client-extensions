from odoo import models


def migrate(cr, version):
    pass


class Group(models.Model):
    _name = "res.groups"
    _inherit = ["res.groups"]
    _module = "base"
    _match_uniq = True
    _match_uniq_warning = (
        "Your existing group '{xmlid}' has been merged with "
        "the standard group that has the same name '{name}'."
        " You should check it to confirm that there is no "
        "security issue."
    )
