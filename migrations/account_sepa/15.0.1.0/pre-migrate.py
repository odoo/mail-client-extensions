from odoo.upgrade import util


def migrate(cr, _version):
    # https://github.com/odoo/enterprise/pull/43806
    # create the new column such that the ORM will not recompute it upon auto_install of account_sepa_pain_001_001_09
    # There is no need to compute it now at all, because none of the existing payments will be linked to a journal
    # that has the new sepa_pain_version set, thus the result of the compute will be to do nothing and let it stay
    # NULL for all existing payments.
    util.create_column(cr, "account_payment", "sepa_uetr", "varchar")
