# Odoo for outlook

## To be able to serve the add-in

- cd to the addin-in sources directory
- `npm install`
- `npm run-script build  -- --env.DOMAIN=127.0.0.1:8080` (replace `127.0.0.1:8080` with the actual domain)
- serve the dist folder

## To add the add-in in outlook for the web

- Open any email
- Click the three dot in the upper right corner of the mail
- Click "Get add-ins"
- Select "My add-ins"
- Click the link "Add a custom add-in"
- Select "Add from URL"
- Paste the URL to the manifest.xml. E.g. https://download.odoo.com/plugins/outlook/manifest.xml

## To pin the add-in

- Click the cog in the upper right corner of the pain window
- Select "View all Outlook settings"
- Click "Mail" > "Customize actions"
- Under the section "Message surface", check "Odoo for Outlook".
