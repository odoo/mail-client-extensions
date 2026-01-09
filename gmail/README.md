# Odoo Gmail Add-on
This addons allows you to find information about the sender of the emails you received
and also to link your Gmail contacts to your Odoo partners, to create leads from Gmail,...

# Development
Create the database and fill the credentials in `consts.ts`
> psql -U root -d postgres -f init_db.sql

To serve the addin, you need a public HTTPS connection to your application.
You cannot use nrgok, because Gmail store all images we use in the addin,
and it won't fetch them if they come from a free ngrok domain name.
So the simplest is to use a VPS (and to do a reverse SSH proxy to develop locally).

Then run
> npm install
> npm run dev

Go to this page:
https://console.cloud.google.com/apis/api/appsmarket-component.googleapis.com/googleapps_sdk_gsao

Then create an HTTP deployment using `deployment.json`, and update the URL in `onTriggerFunction` to contain your ngrok URL.

Then click on "install", and the addin will be available in your Gmail account.

Before committing, run prettier
> npm run prettier

# Production
Update the `CLIENT_ID` and the public URL in `consts.ts`, then run
> npm run build
> node dist
