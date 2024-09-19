from odoo.upgrade import util

PEM_RECOMPUTATION_CRON_CODE = """
keys = env['certificate.key'].search([('pem_key', '=', False)])
certs = env['certificate.certificate'].search([('pem_certificate', '=', False)])
keys._compute_pem_key()
certs._compute_pem_certificate()
self.env['ir.cron']._notify_progress(done=1, remaining=0, deactivate=True)
"""


def migrate(cr, version):
    util.create_cron(
        cr,
        "certificate: recompute PEM content",
        "certificate.certificate",
        PEM_RECOMPUTATION_CRON_CODE,
        interval=(1, "minutes"),
    )
