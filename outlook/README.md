# Odoo for outlook

## General information about the plugin

The plugin allows integration with various Odoo apps and modules like CRM, project ...

The code is based on the [Office Addin API](https://docs.microsoft.com/en-us/office/dev/add-ins/) and
[the react framework](https://reactjs.org/) with typescript.


## To be able to serve the add-in locally for development

- cd to the add-in sources directory
- `npm install`
- `npm run dev-server`


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

## Build for production
Edit `webpack.config.js` and set the production URL in `urlProd`, then run:
> `npm run build`

## Technical remarks

### About translations
The plugin relies on the Odoo database to fetch translations. These translations are fetched during the login process
and then cashed and updated at the plugin's initialization if necessary.

Translations are provided in the `translations_outlook.xml` file located in each of the plugin modules

For more details about translations see: https://github.com/odoo/mail-client-extensions/blob/master/outlook/src/utils/Translator.ts


### Prettier
Before committing, please run prettier to automatically format your code
> `npm run prettier`


### Documentation
- https://learn.microsoft.com/en-us/office/dev/add-ins/quickstarts/outlook-quickstart-yo
- https://storybooks.fluentui.dev/react/?path=/docs/components-text--docs
