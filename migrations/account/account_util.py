from contextlib import contextmanager

from odoo.addons.base.maintenance.migrations import util


@contextmanager
def skip_failing_python_taxes(env, skipped=None):
    if util.module_installed(env.cr, "account_tax_python"):
        origin_compute_amount = env.registry["account.tax"]._compute_amount

        def _compute_amount(self, *args, **kwargs):
            if self.amount_type != "code":
                return origin_compute_amount(self, *args, **kwargs)
            try:
                return origin_compute_amount(self, *args, **kwargs)
            except ValueError as e:
                if skipped is not None:
                    skipped[self.id] = (self.name, e.args[0])
                return 0

        env.registry["account.tax"]._compute_amount = _compute_amount
        yield
        env.registry["account.tax"]._compute_amount = origin_compute_amount
    else:
        yield
