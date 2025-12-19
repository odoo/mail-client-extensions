import { Button, Image, makeStyles } from '@fluentui/react-components'
import { MailCheckmarkRegular, MailRegular } from '@fluentui/react-icons'
import React, { useContext } from 'react'
import { getLoggedState, logEmail } from '../../helpers/log_email'
import { _t } from '../../helpers/translate'
import { Email } from '../../models/email'
import ErrorContext from './Error'

export interface LogEmailProps {
    recordId: number
    model: string
    email: Email
    logEmailTitle: string
    logEmailAlreadyLogged: string
}

const useStyles = makeStyles({
    spinner: {
        padding: '4px',
    },
})

const LogEmail: React.FC<LogEmailProps> = (props: LogEmailProps) => {
    const { recordId, model, email, logEmailTitle, logEmailAlreadyLogged } =
        props
    const showError = useContext(ErrorContext)?.showError
    const styles = useStyles()

    const [isEmailLogged, setIsEmailLogged] = React.useState(() =>
        getLoggedState(recordId, model, email)
    )
    const [isLogging, setIsLogging] = React.useState(() => false)

    const onLogEmail = async () => {
        setIsLogging(true)
        const error = await logEmail(recordId, model, email)
        setIsLogging(false)

        if (error.code) {
            showError(error.message)
            return
        }
        setIsEmailLogged(true)
    }

    if (isLogging) {
        return (
            <Image
                className={styles.spinner}
                width="24px"
                src="assets/spinner.gif"
                alt={_t('Loading')}
            />
        )
    }

    return isEmailLogged ? (
        <Button
            icon={<MailCheckmarkRegular />}
            title={logEmailAlreadyLogged}
            size="small"
            shape="circular"
            appearance="subtle"
            disabled={true}
        />
    ) : (
        <Button
            icon={<MailRegular />}
            title={logEmailTitle}
            size="small"
            shape="circular"
            appearance="subtle"
            onClick={onLogEmail}
        />
    )
}

export default LogEmail
