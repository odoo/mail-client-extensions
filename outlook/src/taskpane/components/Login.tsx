import {
    Button,
    Image,
    Input,
    makeStyles,
    useId,
} from '@fluentui/react-components'
import { CircleHintHalfVerticalRegular } from '@fluentui/react-icons'
import React, { useContext } from 'react'
import {
    exchangeAuthCodeForAccessToken,
    getSupportedAddinVersion,
    openOdooLoginDialog,
} from '../../helpers/http'
import ErrorContext from './Error'

const useStyles = makeStyles({
    loginSection: {
        display: 'flex',
        flexDirection: 'column',
        alignItems: 'center',
        padding: '20px',
        paddingBottom: '30px',
        paddingTop: '10px',
        height: '100%',
    },
    url: {
        width: '100%',
        marginTop: '10px',
    },
    button: {
        width: '100%',
        marginTop: '10px',
    },
    loading: {
        animation: 'spin 4s linear infinite',
    },
})

const Login: React.FC<{
    onLogin: Function
}> = (props) => {
    const styles = useStyles()
    const inputId = useId('input')

    const showError = useContext(ErrorContext)?.showError

    const [url, setUrl] = React.useState(
        () => localStorage.getItem('odoo_url') || ''
    )

    const [loading, setLoading] = React.useState(false)

    const onInputChange = (event: React.ChangeEvent<HTMLInputElement>) => {
        let url = event.target.value
        if (
            url.length &&
            !url.startsWith('http://') &&
            !url.startsWith('https://')
        ) {
            url = 'https://' + url
        }
        setUrl(url)

        if (url.endsWith('/odoo')) {
            url = url.slice(0, -5)
        } else if (url.endsWith('/odoo/web')) {
            url = url.slice(0, -9)
        } else if (url.endsWith('/web')) {
            url = url.slice(0, -4)
        }
        localStorage.setItem('odoo_url', url)
    }

    const onClickLogin = async () => {
        setLoading(true)
        const url = localStorage.getItem('odoo_url')
        const version = await getSupportedAddinVersion(url)
        setLoading(false)
        if (!version) {
            showError(
                'Oops! We could not connect to your database. Make sure the module Mail Plugin is installed in Odoo or contact us at odoo.com/help'
            )
            return
        }

        if (version !== 2) {
            showError(
                'This addin version required Odoo 19.2 or a newer version, please install an older addin version.'
            )
            return
        }

        const authCode = await openOdooLoginDialog(url)
        if (!authCode) {
            showError('Authentication failed')
            return
        }

        const accessToken = await exchangeAuthCodeForAccessToken(url, authCode)
        if (!accessToken) {
            showError('Could not connect get the access token.')
            return
        }

        localStorage.setItem('odoo_access_token', accessToken)
        props.onLogin()
    }

    const onKeyUp = (event: React.KeyboardEvent) => {
        if (event.key === 'Enter') {
            onClickLogin()
        }
    }

    const onClickSignup = () => {
        window.open(
            'https://www.odoo.com/trial?selected_app=mail_plugin:crm:helpdesk:project',
            '_blank'
        )
    }

    const onClickFaq = () => {
        window.open(
            'https://www.odoo.com/documentation/master/applications/productivity/mail_plugins.html',
            '_blank'
        )
    }

    return (
        <section className={styles.loginSection}>
            <Image width="100%" src="assets/login.svg" alt="Login" />
            <Input
                className={styles.url}
                id={inputId}
                value={url}
                placeholder="e.g. mycompany.odoo.com"
                onChange={onInputChange}
                onKeyUp={onKeyUp}
            />
            <Button
                className={styles.button}
                appearance="primary"
                onClick={onClickLogin}
                icon={
                    loading ? (
                        <CircleHintHalfVerticalRegular
                            className={styles.loading}
                        />
                    ) : undefined
                }
            >
                Login
            </Button>
            <Button
                className={styles.button}
                appearance="outline"
                onClick={onClickSignup}
            >
                Sign Up
            </Button>
            <Button
                className={styles.button}
                appearance="transparent"
                onClick={onClickFaq}
            >
                FAQ
            </Button>
        </section>
    )
}

export default Login
