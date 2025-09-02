from odoo.addons.base.maintenance.migrations import util


def migrate(cr, version):
    if util.version_between("14.0", "saas~17.4"):
        util.ensure_mail_alias_mapping(
            cr,
            "documents.share",
            "documents.share_internal_folder",
            "documents.share_internal_folder_mail_alias",
            "inbox",
        )
    if util.version_between("12.0", "saas~17.4"):
        util.ensure_mail_alias_mapping(
            cr,
            "documents.share",
            "documents.share_account_folder",
            "documents.share_account_folder_mail_alias",
            "inbox-financial",
        )
