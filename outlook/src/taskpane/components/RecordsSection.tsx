import { Button, Image, makeStyles } from '@fluentui/react-components'
import { AddRegular, SearchRegular } from '@fluentui/react-icons'
import React from 'react'
import type { OdooRecordType } from '../../../types'
import { getOdooRecordURL } from '../../helpers/http'
import { _t } from '../../helpers/translate'
import { Email } from '../../models/email'
import RecordCard from './RecordCard'

export interface RecordsSectionProps<T extends OdooRecordType> {
    email: Email
    model: string
    logEmailTitle: string
    logEmailAlreadyLogged: string
    searchTitle: string
    sectionTitle: string
    records: T[]
    recordCount: number
    createRecord: Function
    onSearch: Function
    descriptionAttribute: keyof Omit<T, 'id'>
}

const useStyles = makeStyles({
    section: {
        marginTop: '10px',
    },
    header: {
        display: 'flex',
        flexDirection: 'row',
        alignItems: 'center',
        justifyContent: 'space-between',
    },
    title: {
        margin: '5px',
    },
    buttons: {
        display: 'flex',
    },
    button: {
        marginLeft: '5px',
    },
    recordsContainer: {
        display: 'flex',
        flexDirection: 'column',
        justifyContent: 'space-between',
    },
    spinner: {
        padding: '4px',
    },
    showAll: {
        textAlign: 'left',
        display: 'block',
        width: 'fit-content',
        marginLeft: 'calc(5px - var(--spacingHorizontalM))',
    },
})

function RecordsSection<T extends OdooRecordType>(
    props: RecordsSectionProps<T>
) {
    const styles = useStyles()

    const {
        email,
        model,
        logEmailTitle,
        logEmailAlreadyLogged,
        searchTitle,
        sectionTitle,
        records,
        recordCount,
        createRecord,
        onSearch,
        descriptionAttribute,
    } = props

    const [showAll, setShowAll] = React.useState(false)

    const _records = showAll ? records : [...records].splice(0, 5)

    const [isCreating, setIsCreating] = React.useState(false)

    const onOpen = (record: OdooRecordType) => {
        window.open(getOdooRecordURL(model, record.id))
    }

    const items = _records.map((record, _index) => (
        <RecordCard
            key={`${record.id}-${model}`}
            model={model}
            onClick={() => onOpen(record)}
            record={record}
            description={record[descriptionAttribute] as string}
            name={record.name}
            logEmail={true}
            logEmailTitle={logEmailTitle}
            logEmailAlreadyLogged={logEmailAlreadyLogged}
            email={email}
        />
    ))

    const onCreate = async () => {
        setIsCreating(true)
        await createRecord()
        setIsCreating(false)
    }

    return (
        <section className={styles.section}>
            <div className={styles.header}>
                <h4 className={styles.title}>{sectionTitle}</h4>
                <div className={styles.buttons}>
                    {isCreating ? (
                        <Image
                            className={styles.spinner}
                            width="24px"
                            src="assets/spinner.gif"
                            alt={_t('Loading')}
                        />
                    ) : (
                        <Button
                            className={styles.button}
                            icon={<AddRegular />}
                            title={_t('New')}
                            size="small"
                            appearance="subtle"
                            shape="circular"
                            onClick={onCreate}
                        />
                    )}
                    <Button
                        className={styles.button}
                        icon={<SearchRegular />}
                        title={searchTitle}
                        size="small"
                        appearance="subtle"
                        shape="circular"
                        onClick={() => onSearch()}
                    />
                </div>
            </div>
            <div className={styles.recordsContainer}>
                {items}
                {_records.length < recordCount && (
                    <Button
                        className={styles.showAll}
                        appearance="subtle"
                        onClick={() => {
                            setShowAll(true)
                        }}
                    >
                        {_t('Show all')}
                    </Button>
                )}
            </div>
        </section>
    )
}

export default RecordsSection
