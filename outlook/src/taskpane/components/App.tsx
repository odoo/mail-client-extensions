import { Button, makeStyles } from '@fluentui/react-components'
import { ArrowLeftRegular } from '@fluentui/react-icons'
import * as React from 'react'
import { _t, fetchTranslations } from '../../helpers/translate'
import { Email } from '../../models/email'
import { Partner } from '../../models/partner'
import Error, { showError } from './Error'
import GlobalLoading, {
    hideGlobalLoading,
    showGlobalLoading,
} from './GlobalLoading'
import Loading from './Loading'
import Login from './Login'
import PartnerView from './PartnerView'
import SearchRecords from './SearchRecords'

interface AppProps {}

const useStyles = makeStyles({
    root: {
        minHeight: '100vh',
        padding: '0 10px',
    },
    header: {
        display: 'flex',
        flexDirection: 'row',
        justifyContent: 'space-between',
        alignItems: 'center',
    },
    goBack: {
        marginTop: '5px',
    },
    subTitle: {
        marginBottom: '5px',
        marginTop: '5px',
        marginLeft: '10px',
    },
})

const App: React.FC<AppProps> = (_props: AppProps) => {
    const styles = useStyles()

    const [loading, setLoading] = React.useState(
        !!localStorage.getItem('odoo_access_token')
    )

    // pages used to go back
    const [currentPage, setCurrentPage] = React.useState(null)
    const [pages, setPages] = React.useState(() => [])

    const email = new Email()

    const pushPage = (page) => {
        setPages((prevPages) => [...prevPages, page])
        setCurrentPage(page)
    }

    /**
     * Search partners in the database.
     */
    const searchPartners = async (query: string): Promise<Partner[]> => {
        const [searchedPartners, error] = await Partner.searchPartner(query)
        if (error.code) {
            showError(error.message)
            return []
        }
        return searchedPartners
    }

    /**
     * Open the view to search a contact.
     */
    const onSearchPartners = () => {
        pushPage(
            <SearchRecords
                onClick={setPartner}
                search={searchPartners}
                model="res.partner"
                searchPlaceholder={_t('Search contact')}
                iconAttribute="image"
                records={[]}
                nameAttribute="name"
                descriptionAttribute="description"
                email={email}
            />
        )
    }

    const logout = () => {
        setLoading(false)
        localStorage.removeItem('odoo_access_token')
        setPages([])
        setCurrentPage(<Login onLogin={loadEmailContacts} />)
    }

    /**
     * Open the given partner and fetch the leads, tasks, tickets, etc
     */
    const setPartner = async (partner: Partner) => {
        // set the info we know as soon as possible
        pushPage(
            <PartnerView
                key={`partner-${partner.key}`}
                partner={partner}
                email={email}
                onLogout={logout}
                onSearch={onSearchPartners}
                pushPage={pushPage}
                goBack={goBack}
                updatePartner={updatePartner}
            />
        )

        // fetch the leads, tickets, tasks, etc
        showGlobalLoading()
        const [newPartner, error] = await Partner.getPartner(
            partner.name,
            partner.email,
            partner.id
        )
        hideGlobalLoading()
        if (error.code) {
            showError(error.message)
            return
        }
        updatePartner(newPartner)
    }

    /**
     * Assuming that the current card is the partner view, update it.
     */
    const updatePartner = (partner: Partner) => {
        const newCard = (
            <PartnerView
                key={`partner-${partner.key}`}
                partner={partner}
                email={email}
                onLogout={logout}
                onSearch={onSearchPartners}
                pushPage={pushPage}
                goBack={goBack}
                updatePartner={updatePartner}
            />
        )

        setPages((prevPages) => [...prevPages.slice(0, -1), newCard])
        setCurrentPage(newCard)
    }

    const bottom = (
        <h4 className={styles.subTitle}>{_t('In this conversation')}</h4>
    )

    /**
     * Show the contacts in the current email.
     */
    const setEmailContacts = (partners: Partner[]) => {
        const searchRecords = (
            <SearchRecords
                onClick={setPartner}
                search={searchPartners}
                model="res.partner"
                bottom={bottom}
                searchPlaceholder={_t('Search contact')}
                iconAttribute="image"
                records={partners}
                nameAttribute="name"
                descriptionAttribute="description"
                email={email}
            />
        )
        setPages([searchRecords])
        setCurrentPage(searchRecords)
    }

    /**
     * Fetch the information about the contact in the email.
     * (to know if they exist in the database...)
     */
    const loadEmailContacts = async () => {
        const token = localStorage.getItem('odoo_access_token')
        if (!token?.length) {
            logout()
            return
        }

        const [searchedPartners, error] = await Partner.searchPartner(
            email.contacts.map((c) => c.email)
        )
        if (error.code) {
            logout()
            return
        }

        const existingPartnersEmails = searchedPartners.map((p) => p.email)
        for (const contact of email.contacts) {
            if (existingPartnersEmails.includes(contact.email)) {
                continue
            }
            searchedPartners.push(
                Partner.fromOdooResponse({
                    name: contact.name,
                    email: contact.email,
                })
            )
        }

        fetchTranslations()
        setEmailContacts(searchedPartners)
        if (searchedPartners.length === 1) {
            setPartner(searchedPartners[0])
        }

        setLoading(false)
    }

    const goBack = (backCount: number = 1) => {
        setPages((prevPages) => {
            const page = prevPages[prevPages.length - 1 - backCount]
            setCurrentPage(page)
            return prevPages.slice(0, prevPages.length - backCount)
        })
    }

    // set the logged state if needed, without blocking the rendering
    React.useEffect(() => {
        loadEmailContacts()
    }, [])

    return (
        <div className={styles.root}>
            <div className={styles.header}>
                {pages.length > 1 && (
                    <Button
                        className={styles.goBack}
                        icon={<ArrowLeftRegular />}
                        title={_t('Go back')}
                        size="small"
                        shape="circular"
                        appearance="subtle"
                        onClick={() => goBack()}
                    />
                )}
                <GlobalLoading />
            </div>
            {loading ? <Loading /> : currentPage}
            <Error />
        </div>
    )
}

export default App
