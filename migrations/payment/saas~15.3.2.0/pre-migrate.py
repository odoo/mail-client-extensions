from odoo.upgrade import util


def migrate(cr, version):
    util.remove_field(cr, "payment.acquirer.onboarding.wizard", "stripe_secret_key")
    util.remove_field(cr, "payment.acquirer.onboarding.wizard", "stripe_publishable_key")

    util.remove_record(cr, "payment.action_open_payment_onboarding_payment_acquirer_wizard")
    util.remove_view(cr, "payment.onboarding_payment_acquirer_step")
    cr.execute(
        "create index tmp_mig_epaymenttransactioncall_speedup_idx on payment_transaction(callback_model_id,callback_res_id)"
    )
    util.ENVIRON["__created_fk_idx"].append("tmp_mig_epaymenttransactioncall_speedup_idx")
