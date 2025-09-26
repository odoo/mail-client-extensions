from odoo.addons.base.maintenance.migrations import util


def migrate(cr, version):
    util.ENVIRON["_no_orm_table_change"] |= {
        "documents.document",
        # models removed in 18.0
        "documents.folder",
        "documents.share",
    }
