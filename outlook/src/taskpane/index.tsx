import { FluentProvider, createLightTheme } from '@fluentui/react-components'
import React from 'react'
import { createRoot } from 'react-dom/client'
import App from './components/App'
import { ErrorProvider } from './components/Error'

/* global document, Office, module, require, HTMLElement */

const rootElement: HTMLElement | null = document.getElementById('container')
const root = rootElement ? createRoot(rootElement) : undefined

// https://aka.ms/themedesigner-v9
export const odooTheme = createLightTheme({
    10: '#000000',
    20: '#181216',
    30: '#281D25',
    40: '#392835',
    50: '#4C3445',
    60: '#5F3F56',
    70: '#724C68',
    80: '#825B78',
    90: '#926B87',
    100: '#A17C97',
    110: '#B08DA6',
    120: '#BF9FB5',
    130: '#CDB1C5',
    140: '#DAC4D4',
    150: '#E7D7E2',
    160: '#F4EBF1',
})

function render() {
    root?.render(
        <FluentProvider theme={odooTheme}>
            <ErrorProvider>
                <App />
            </ErrorProvider>
        </FluentProvider>
    )
}

/* Render application after Office initializes */
Office.onReady(() => {
    Office.context.mailbox.addHandlerAsync(
        /* On desktop, when we open a new email while keeping the addin open. */
        Office.EventType.ItemChanged,
        () => {
            window.dispatchEvent(new CustomEvent('newEmailOpened'))
        }
    )
    render()
})

if ((module as any).hot) {
    ;(module as any).hot.accept('./components/App', () => {
        render()
    })
}
