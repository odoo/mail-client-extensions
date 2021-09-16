# Odoo for outlook

## General information about the plugin

The plugin allows integration with various Odoo apps and modules like CRM, project ...

The code is based on the [Office Addin API](https://docs.microsoft.com/en-us/office/dev/add-ins/) and 
[the react framework](https://reactjs.org/) with typescript.


## To be able to serve the add-in locally for development

- cd to the add-in sources directory
- `npm install`
- `npm run-script dev-server`

## To be able to use, test and debug the plugin with a linux OS

- cd to the add-in sources directory
- `npm install`
- open the `node_modules/office-addin-dev-certs/lib/verify.js` file
- inside the file, in the switch clause located in the `getVerifyCommand()` function add the following :

```bash
case "linux":
    return `[ -f /usr/local/share/ca-certificates/office-addin-dev-certs/${defaults.caCertificateFileName} ] && openssl x509 -in /usr/local/share/ca-certificates/office-addin-dev-certs/${defaults.caCertificateFileName} -checkend 86400 -noout`;
```

- open the `node_modules/office-addin-dev-certs/lib/install.js` file
- inside the file, in the switch clause add the following:

```bash
case "linux":
   return `sudo cp ${caCertificatePath} /usr/local/share/ca-certificates && sudo /usr/sbin/update-ca-certificates`;
```

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

## Technical remarks

### About translations
The plugin relies on the Odoo database to fetch translations. These translations are fetched during the login process 
and then cashed and updated at the plugin's initialization if necessary.

Translations are provided in the `translations_outlook.xml` file located in each of the plugin modules

For more details about translations see: https://github.com/odoo/mail-client-extensions/blob/master/outlook/src/utils/Translator.ts

### Prettier
Before committing, please run prettier to automatically format your code
> `npm run-script prettier`

### Deploy on Github Page
Github provides a service to host static website. It can be used to serve the files of
the add-in and so to serve the add-in for testing.

First build the add-in
> `npm run-script build`

Then replace the default domain (localhost) of the add-in by the domain of your Github Page
> `./replaceDomain.sh <domain>`

Then publish it
> `npm run-script deploy -- -r <repository> -b <branch>`
