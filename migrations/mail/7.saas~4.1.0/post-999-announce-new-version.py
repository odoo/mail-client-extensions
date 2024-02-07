# -*- coding: utf-8 -*-
from openerp.addons.base.maintenance.migrations import util


def migrate(cr, version):
    # NOTE message is in RST
    message = """
.. |br| raw:: html

    <br />

- Website Features:

  + Website Translation: with the new `website_gengo`, you can now translate
    your website automatically through the gengo web service.

  + Website Forum: QA forum on your website. Get rewarded to provide the best
    answers to your customers questions. Seamlessly integrated with the
    gamification module, you can earn reward by responding questions or voting
    for best answers.

  + Website Twitter: Display your favorite tweets on your website.

  + Mailing List Archives: Display your public mail groups on your website.

- Mass Mailing: Better statistics about sent mails.

- Survey: the survey module has completely been rewritten and is now fully
  integrated into the website.

- New Reporting Engine: new reporting engine based on QWeb, allowing easier
  customization through the website. This new engine also has a better and
  faster PDF rendering. All accounting, sale, purchase, MRP and HR reports
  have been rewritten.

- Misc improvements:

  + More language available for translation via gengo.
  + New module `crm_project_issue` which allows creation of issues from leads.

"""
    util.announce(cr, "7.saas~4", message)


if __name__ == "__main__":
    # openerp must be in PYTHONPATH
    def echo(_cr, version, message):
        print(util.rst2html(message))  # noqa: T201

    util.announce = echo
    migrate(None, None)
