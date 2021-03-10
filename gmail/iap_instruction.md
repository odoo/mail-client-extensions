# Shared secret between IAP and the add-on
Go to your Google project,
> clasp open

Then File ->  Project properties -> Script Properties

And add a row,
> `ODOO_SHARED_SECRET` `<your shared secret>`

On the IAP side, add a system parameter
> `iap_mail_extension.shared_secret` `<your shared secret>`

This secret will allow the add-on to authenticate to IAP.
