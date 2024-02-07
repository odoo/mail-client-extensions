# -*- coding: utf-8 -*-
from openerp.addons.base.maintenance.migrations import util


def migrate(cr, version):
    # NOTE message is in RST
    message = """
        .. |br| raw:: html

            <br />

        * **New Sales Teams Dashboard**, presenting graphical statistics (sparklines, gauges) on your monthly teams activities (CRM pipeline, Quotes, Invoices). Available when Sales Teams management is enabled in the Sales Configuration Settings.
        * **Dynamic stages** on leads, opportunities, tasks, issues and job applicants. You now have even more freedom to define your workflows, and the redundant *status* field is gone. In the kanban view you can define and reorder stages using drag and drop, fold or unfold them, etc. The screens and filters have been adapted to match your stages everywhere.
          |br| **Watch out!** when you open a lead/opportunity/task/issue/applicant, you must now use the clickable stage bar to change the stage! See `this example <http://i.imgur.com/fxcex6q.png>`_.
        * **Improved Google Doc integration**. The new **Google Spreadsheet** module allows one-click creation of report spreadsheets, providing dedicated OpenERP formulas to grab live data from your OpenERP system and construct any kind of custom reportings.
        * **New** `Mass-Mailing App <https://www.openerp.com/apps/mass_mailing/>`_ provides automated mass-mailing campaigns based on email templates. Use it qualify your Leads, send newsletters to your customers, or any similar mass-mailing task. Graphical dashboards give your real time statistics on campaign performance to improve your conversion rate, tracking mails sent, received, bounced, opened and answered.
          |br| *Note*: this is a new App, the `Marketing Campaigns <https://www.openerp.com/apps/marketing_campaign/>`_ App still provides advanced Lead Automation with customizable workflows. We're now working on improving the integration between these two Apps so both get the same statistics and dashboards.
        * **Updated Geolocation tools**. The updated CRM Geolocation App offers an improved assistant for assigning/forwarding Leads to local partners, with a live preview of the results.
        * **Improved Leave Requests**. When confirming new Leaves requests, other leave requests waiting for validation are now taken into account in order to display the remaining leaves, helping employees avoid mistakes. HR Officers are also able to re-edit existing leaves request much more easily.
        * **Social HR**. It is now possible to follow the status of your fellow colleagues, receiving notification whenever they post a message to their followers. Suggestions for colleagues to follow are displayed in your OpenERP Inbox.
        * **Simplified Sales Orders**. The former Sales Shop object has been removed in order to simplify the Sales process. The pricelist and destination warehouse can now be selected directly on the Sales order, when relevant.
        * You can now **choose the desired currency directly on Purchase Orders**, when multi-currency mode is enabled in the settings.
        * **New Customers/Suppliers Merge assistant**. Available via the new *Automatic Merge* option in the *More* menu of the Customers and Suppliers lists, this advanced tool helps you merge duplicate entries. I will automatically update all documents to link to the merged entry.
        * **Automated actions and Server Actions revamped**, with a drastically improved and simplified user interface.
        * Plus a ton of various performance improvements and smaller bugfixes...
    """
    util.announce(cr, "7.saas~2", message)


if __name__ == "__main__":
    # openerp must be in PYTHONPATH
    def echo(_cr, version, message):
        print(util.rst2html(message))  # noqa: T201

    util.announce = echo
    migrate(None, None)
