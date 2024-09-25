from odoo import models

from odoo.addons.base.maintenance.migrations import util

try:
    from odoo.addons.documents.models import tags  # noqa
except ImportError:
    from odoo.addons.documents.models import documents_tag  # noqa


def migrate(cr, version):
    pass


class Tags(models.Model):
    _inherit = "documents.tag"
    _module = "documents"
    _match_uniq = True


if not util.version_gte("17.5"):

    class TagsCategories(models.Model):
        _inherit = "documents.facet"
        _module = "documents"
        _match_uniq = True
