from odoo import models

try:
    import odoo.addons.gamification.models.challenge as _ignore
except ImportError:
    import odoo.addons.gamification.models.gamification_challenge as _ignore

try:
    import odoo.addons.gamification.models.res_users as _ignore  # noqa
except ImportError:
    # This file appears in odoo/odoo@3b9dcb6d8d8c50000828f3503e69c567d0daa98c
    # in which the method `_rank_changed` didn't exist.
    # We still define the method even nobody will ever call it.
    pass


def migrate(cr, version):
    pass


class Challenge(models.Model):
    _name = "gamification.challenge"
    _inherit = ["gamification.challenge"]
    _module = "gamification"

    def _recompute_challenge_users(self):
        return True

    def _generate_goals_from_challenge(self):
        return True


class ResUsers(models.Model):
    _inherit = "res.users"
    _module = "gamification"

    def _rank_changed(self):
        # avoid sending emails on karma ranks creation
        pass
