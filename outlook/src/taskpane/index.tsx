import 'office-ui-fabric-react/dist/css/fabric.min.css';
import App from './components/App';
import { AppContainer } from 'react-hot-loader';
import { initializeIcons } from 'office-ui-fabric-react/lib/Icons';
import * as React from 'react';
import * as ReactDOM from 'react-dom';
import { Authenticator } from '@microsoft/office-js-helpers';

initializeIcons();

let isOfficeInitialized = false;

const title = 'Odoo for Outlook';

const render = (Component) => {
    ReactDOM.render(
        <AppContainer>
            <Component
                title={title}
                isOfficeInitialized={isOfficeInitialized}
                itemChangedRegister={itemChangedRegister}
            />
        </AppContainer>,
        document.getElementById('container'),
    );
};

let itemChangedHandler: (type: Office.EventType) => void;
const itemChangedRegister = (f: (type: Office.EventType) => void) => {
    itemChangedHandler = f;
};

/* Render application after Office initializes */
Office.initialize = () => {
    if (Authenticator.isAuthDialog()) return;
    isOfficeInitialized = true;
    Office.context.mailbox.addHandlerAsync(Office.EventType.ItemChanged, itemChangedHandler);
    render(App);
};

/* Initial render showing a progress bar */
render(App);

if ((module as any).hot) {
    (module as any).hot.accept('./components/App', () => {
        const NextApp = require('./components/App').default;
        render(NextApp);
    });
}
