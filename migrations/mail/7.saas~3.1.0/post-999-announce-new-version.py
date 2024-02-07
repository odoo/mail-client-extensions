# -*- coding: utf-8 -*-
from openerp.addons.base.maintenance.migrations import util


def migrate(cr, version):
    # NOTE message is in RST
    message = """
.. |br| raw:: html

    <br />

- Website Features:

  + Website Builder: Create beautiful websites with no technical knowledge.
    OpenERP's unique 'edit inline' approach makes website creation
    surprisingly easy. No more complex backend; just click anywhere
    to change any content.

  + eCommerce: OpenERP's unique Website Builder makes product pages creation
    surprisingly easy.
    "Want to change the price of a product? or put it in bold?
    Want to add a banner for a specific product?" just click and change.
    What you see is what you get.

  + Blogs: Express yourself with the OpenERP enterprise grade blogging
    platform. Write beautiful blog posts, engage with visitors, translate
    content and moderate social streams. Get your blog posts efficiently
    referenced in Google and translated into mutiple languages in just
    a few clicks.

  + Online Events: Organize, promote and sell events online using all the
    great tools of the Website Builder.

  + Human Resources recruitment management: Publish sexy job positions
    description and let applicants apply in few clicks directly from your
    website. Describe jobs with the power of attractive blocks.
    With attractive job position you will increase the application form and
    give you the best chance to hire the best employee.

- Online Quotation templates: create quotation templates using website builder
  blocks, and send attractive quotations to your customers.
  They receive a link to read the quotation, and can directly accept
  or refuse it, or discuss it with you.

- Gamification: The gamification App provides ways to evaluate and motivate
  people. The users can be evaluated using goals and numerical objectives
  Goals are assigned through challenges to evaluate and compare members of a
  team over time. Non-numerical achievements can be rewarded with badges.
  From a simple "thank you" to an exceptional achievement, a badge is an easy
  way to congratulate and thank an employee for their good work.

- Point of Sales: The POS has been upgraded with the latest POSBox compatibilty
  and features. This affordable solution integrates smoothly with modern and
  standard hardware like tablets, barcode scanners, receipt printers, cash
  registers and scales

- Calendar and Google Sync: enjoy the revamped calendar and the built-in
  synchronization with your google calendar.

- Improved Reporting: the reporting features of all Apps have been upgraded
  to a new dynamic Business Intelligence tool that provides multi-dimensional
  pivot table features, heat map, and much more. Head over to the Reporting
  menu and give it a go!

- Misc improvements:

  + HR: Manage Resumes and Letters directly from recruitment menu
  + Updated privacy settings for OpenChatter:

    * Discussion: visible for everyone
    * Log a Note: visible by employees (user with employee group)
    * History (all other logs): visible by everyone regarding subtypes and mail settings

  + Kanban columns: Drag and drop your tasks/opportunities/applicants in folded columns
  + Choose font for RML reports: in General Settings, load and choose fonts for
    PDF reports (allows supporting CJK/Asian languages)

"""
    util.announce(cr, "7.saas~3", message)


if __name__ == "__main__":
    # openerp must be in PYTHONPATH
    def echo(_cr, version, message):
        print(util.rst2html(message))  # noqa: T201

    util.announce = echo
    migrate(None, None)
