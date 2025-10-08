import { Button, Image, Input, makeStyles } from '@fluentui/react-components'
import { SearchRegular } from '@fluentui/react-icons'
import * as React from 'react'
import { _t } from '../../helpers/translate'
import { Email } from '../../models/email'
import RecordCard from './RecordCard'
import SearchNoRecord from './SearchNoRecord'

export interface SearchRecordsProps {
    model: string
    title?: string
    bottom?: any
    searchPlaceholder: string
    records: any[]
    nameAttribute: string
    descriptionAttribute: string
    iconAttribute?: string
    onClick: Function
    search: Function
    loading?: boolean // can be used if we need an initial search
    // Log email
    email?: Email
    logEmail?: boolean
    logEmailTitle?: string
    logEmailAlreadyLogged?: string
}

const useStyles = makeStyles({
    container: {
        display: 'flex',
        flexDirection: 'column',
        paddingTop: '5px',
    },
    title: {
        marginBottom: '5px',
        marginTop: '5px',
    },
    input: {
        width: 'calc(100% - 40px)',
        marginBottom: '5px',
    },
    searchContainer: {
        display: 'flex',
        flexDirection: 'row',
        justifyContent: 'space-between',
        alignItems: 'flex-start',
    },
    spinner: {
        padding: '8px',
    },
})

const SearchRecords: React.FC<SearchRecordsProps> = (
    props: SearchRecordsProps
) => {
    const {
        descriptionAttribute,
        iconAttribute,
        model,
        nameAttribute,
        onClick,
        search,
        records: _records,
        searchPlaceholder,
        title,
        bottom,
        email,
        logEmail,
        logEmailTitle,
        logEmailAlreadyLogged,
        loading: _loading,
    } = props
    const styles = useStyles()

    const [records, setRecords] = React.useState(_records)
    const [query, setQuery] = React.useState('')
    const [loading, setLoading] = React.useState(_loading)
    const [initSearch, setInitSearch] = React.useState(true)

    const onSearch = async () => {
        setLoading(true)
        setRecords((await search(query)) || [])
        setLoading(false)
        setInitSearch(false)
    }

    const onKeyUp = (event) => {
        if (event.key === 'Enter') {
            onSearch()
        }
    }

    const items = records.map((record, _index) => (
        <RecordCard
            key={`${record.id}-${model}-${record.email}-${record.name}`}
            model={model}
            onClick={onClick}
            record={record}
            description={record[descriptionAttribute]}
            icon={record[iconAttribute]}
            name={record[nameAttribute]}
            email={email}
            logEmail={logEmail}
            logEmailTitle={logEmailTitle}
            logEmailAlreadyLogged={logEmailAlreadyLogged}
        />
    ))

    return (
        <div className={styles.container}>
            {title && <h4 className={styles.title}>{title}</h4>}
            <div className={styles.searchContainer}>
                <Input
                    className={styles.input}
                    value={query}
                    placeholder={searchPlaceholder}
                    onChange={(e) => setQuery(e.target.value)}
                    onKeyUp={onKeyUp}
                />
                {loading ? (
                    <Image
                        className={styles.spinner}
                        width="32px"
                        src="assets/spinner.gif"
                        alt={_t('Loading')}
                    />
                ) : (
                    <Button icon={<SearchRegular />} onClick={onSearch} />
                )}
            </div>
            {initSearch && bottom}
            {items.length || initSearch ? (
                <div>{items}</div>
            ) : (
                <SearchNoRecord />
            )}
        </div>
    )
}

export default SearchRecords
