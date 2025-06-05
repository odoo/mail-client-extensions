from odoo.upgrade import util

documents_18_5_pre_migrate = util.import_script("documents/saas~18.5.1.4/pre-migrate.py")


def migrate(cr, version):
    documents_18_5_pre_migrate.wrap_documents_server_action(
        cr,
        "documents_hr_expense.ir_actions_server_create_hr_expense",
    )
