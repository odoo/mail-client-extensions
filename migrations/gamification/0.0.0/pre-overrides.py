from odoo import models
import odoo.addons.gamification.models.challenge as _ignore  # noqa


def migrate(cr, version):
    pass


class Challenge(models.Model):
    _inherit = "gamification.challenge"
    _module = "gamification"

    def _recompute_challenge_users(self):
        return True

    def _generate_goals_from_challenge(self):
        return True
