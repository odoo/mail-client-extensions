# Odoo Gmail Add-on
This addons allows you to find information about the sender of the emails you received
and also to link your Gmail contacts to your Odoo partners, to create leads from Gmail,...

![Odoo Gmail Extension](./assets/img/readme.png)

# Development
## Requirements
First you need npm,
> apt-get install -y npm

Install the dependencies
> npm install

## Prettier
You should auto-format the code using the prettier configuration,
> `npx prettier --config .prettierrc 'src/**/*.ts' --write`

## Compiling

We use [rollup.js](https://github.com/rollup/rollup) to package all of the source files into a single one.
This is necessary as App Scripts do not support ES6 import/export statements yet.

Once you have applied the necessary changes, run the following command:
> npx rollup -c

This will simultaneously compile and package the typescript sourcecode inside `build/main.js`

Now all you need to do is upload the script to your account and deploy it!

## Uploading method 1: Manually copying the file
If you do not plan on updating this script regularly, perhaps you will prefer using Google's GUI.

- Head to [the App Scripts manager](https://script.google.com/) and create a project
- Go to the project settings and enable appscript.json editing: `Show "appsscript.json" manifest file in editor`
- Copy the contents of your local `appscript.json` to the remote one in the project editor
- Create a file `main.gs` and remove the existing `Code.gs` if any.
- Copy the contents of your local `build/main.js` to the `main.gs` file in the project editor

## Uploading method 2: Using Clasp
You may want to use the Google's CLI tool [clasp](https://github.com/google/clasp) to manage, compile and update your app script.

First install
> npm install -g @google/clasp

Login to your account to be able to push on your Gmail project,
> clasp login

Note: the `--no-localhost` option we previously recommended was [deprecated by google](https://developers.google.com/identity/protocols/oauth2/resources/oob-migration)

### If you already have a project
Update `.clasp.json` to use your own script id and project.
If you do not have a specific project, use `Default`.

### If you do not have a project yet
Remove `.clasp.json`

Create a project
> clasp create

For the project type, select "api".

### Push your project
Push the project
> clasp push


# Deployment
Finally, you can enable the add-on for your account.

Head to [the App Scripts manager](https://script.google.com/).
- Select your project and click "Deploy".
- For testing on your account just select "Test deployments". "Google Workspace Add-on" should be automatically selected as the type.
- Click "Install" and the add-on should appear in the addons tab of Gmail.

You're done!

For final deployments you will need to create a Google Cloud Project with the GMail API and link it to this script.
Refer to Google's documentation for more information.

# Documentation
`GmailApp` object,
https://developers.google.com/apps-script/reference/gmail/gmail-app

`URL fetch API`
https://developers.google.com/apps-script/reference/url-fetch

`Storage`
https://developers.google.com/apps-script/reference/cache
https://developers.google.com/apps-script/reference/properties
