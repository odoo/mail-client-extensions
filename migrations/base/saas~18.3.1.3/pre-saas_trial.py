from odoo.upgrade import util


def migrate(cr, version):
    util.remove_view(cr, "saas_trial.users_form_view")
