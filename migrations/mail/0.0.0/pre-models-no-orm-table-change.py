from odoo.addons.base.maintenance.migrations import util


def migrate(cr, version):
    util.ENVIRON["_no_orm_table_change"] |= {
        "mail.activity",
        "mail.followers",
        "mail.message",
        "mail.tracking.value",
        "discuss.channel",
        "discuss.channel.member",
    }
