import { makeStyles } from '@fluentui/react-components'
import React from 'react'
import type { OdooRecordType } from '../../../types'
import { Email } from '../../models/email'
import LogEmail from './LogEmail'

export interface RecordCardProps {
    model: string
    record: OdooRecordType
    name: string
    description: string | React.JSX.Element | React.JSX.Element[]
    icon?: string
    onClick?: Function
    // Log email
    email?: Email
    logEmail?: boolean
    logEmailTitle?: string
    logEmailAlreadyLogged?: string
}

const useStyles = makeStyles({
    container: {
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'space-between',
        width: '100%',
    },
    record: {
        overflow: 'hidden',
        userSelect: 'none',
        display: 'flex',
        borderRadius: '5px',
        padding: '5px',
        width: '100%',
        '&.clickable': {
            cursor: 'pointer',
        },
        '&.clickable:hover': {
            background: '#f5f5f5',
        },
        '&.clickable:active': {
            background: '#e0e0e1',
        },
    },
    recordInfo: {
        width: '100%;',
        overflow: 'hidden',
        display: 'flex',
        flexDirection: 'column',
        justifyContent: 'center',
    },
    info: {
        maxWidth: '100%',
        overflow: 'hidden',
        whiteSpace: 'nowrap',
        textOverflow: 'ellipsis',
    },
    icon: {
        width: '40px',
        height: '40px',
        borderRadius: '50%',
        marginRight: '5px',
    },
    description: {
        fontSize: '0.8rem',
        display: 'flex',
        flexDirection: 'column',
        '& > span, &': {
            maxWidth: '100%',
            overflow: 'hidden',
            whiteSpace: 'nowrap',
            textOverflow: 'ellipsis',
            display: 'block',
        },
    },
})

const RecordCard: React.FC<RecordCardProps> = (props: RecordCardProps) => {
    const {
        description,
        icon,
        model,
        name,
        onClick,
        record,
        logEmail,
        logEmailTitle,
        logEmailAlreadyLogged,
        email,
    } = props
    const styles = useStyles()

    return (
        <div className={styles.container}>
            <div
                className={styles.record + (onClick && ' clickable')}
                onClick={onClick && (() => onClick(record))}
            >
                {!!icon && <img className={styles.icon} src={icon} />}
                <div className={styles.recordInfo}>
                    <span
                        className={styles.info}
                        title={typeof name === 'string' ? name : ''}
                    >
                        {name}
                    </span>
                    <div
                        className={styles.description}
                        title={
                            typeof description === 'string' ? description : ''
                        }
                    >
                        {description}
                    </div>
                </div>
            </div>
            {logEmail && (
                <LogEmail
                    recordId={record.id}
                    model={model}
                    email={email}
                    logEmailTitle={logEmailTitle}
                    logEmailAlreadyLogged={logEmailAlreadyLogged}
                />
            )}
        </div>
    )
}

export default RecordCard
