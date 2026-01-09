import {
    Button,
    makeStyles,
    Menu,
    MenuButton,
    MenuItem,
    MenuList,
    MenuPopover,
    MenuTrigger,
} from '@fluentui/react-components'
import {
    ArrowClockwiseRegular,
    ArrowLeftRegular,
    MoreVerticalRegular,
    SignOutRegular,
} from '@fluentui/react-icons'
import React, { useContext } from 'react'
import { _t, fetchTranslations } from '../../helpers/translate'
import { Email } from '../../models/email'
import { Partner } from '../../models/partner'
import ErrorContext from './Error'
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
    spinner: {
        padding: '4px',
    },
    kebab: {
        minWidth: '0',
    },
    kebabButton: {
        '& div': {
            display: 'flex',
            flexDirection: 'row',
            alignItems: 'center',
            justifyContent: 'space-between',
            '& > span': {
                marginRight: '5px',
            },
        },
    },
})

const App: React.FC<AppProps> = (_props: AppProps) => {
    const styles = useStyles()
    const showError = useContext(ErrorContext)?.showError

    const [loading, setLoading] = React.useState(
        !!localStorage.getItem('odoo_access_token')
    )
    const [logged, setLogged] = React.useState(false)

    // pages used to go back
    const [currentPage, setCurrentPage] =
        React.useState<React.JSX.Element | null>(null)
    const [pagesPartner, setPagesPartner] =
        React.useState<[React.JSX.Element, Partner][]>()

    let email = new Email()

    const pushPage = (page: React.JSX.Element, partner: Partner = null) => {
        setPagesPartner((prevPages) => [...prevPages, [page, partner]])
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
            <SearchRecords<Partner>
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
        setLogged(false)
        localStorage.removeItem('odoo_access_token')
        setPagesPartner([])
        setCurrentPage(<Login onLogin={loadEmailContacts} />)
    }

    /**
     * Open the given partner and fetch the leads, tasks, tickets, etc.
     */
    const setPartner = async (partner: Partner) => {
        // set the info we know as soon as possible
        pushPage(
            <PartnerView
                key={`partner-${partner.key}`}
                partner={partner}
                email={email}
                onSearch={onSearchPartners}
                pushPage={pushPage}
                goBack={goBack}
                updatePartner={updatePartner}
            />,
            partner
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
                onSearch={onSearchPartners}
                pushPage={pushPage}
                goBack={goBack}
                updatePartner={updatePartner}
            />
        )

        setPagesPartner((prevPages) => [
            ...prevPages.slice(0, -1),
            [newCard, partner],
        ])
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
        setPagesPartner([[searchRecords, null]])
        setCurrentPage(searchRecords)
    }

    /**
     * Fetch the information about the contact in the email.
     * (to know if they exist in the database...)
     */
    const loadEmailContacts = async (autoOpen = true) => {
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
        if (searchedPartners.length === 1 && autoOpen) {
            setPartner(searchedPartners[0])
        }

        setLogged(true)
        setLoading(false)
    }

    const goBack = (backCount: number = 1) => {
        setPagesPartner((prevPages) => {
            if (prevPages.length === 2) {
                // the contact could have been created, reload the view
                setTimeout(() => loadEmailContacts(false))
                return []
            }
            const [page, _partner] = prevPages[prevPages.length - 1 - backCount]
            setCurrentPage(page)
            return prevPages.slice(0, prevPages.length - backCount)
        })
    }

    const onRefresh = async () => {
        const partner = pagesPartner[pagesPartner.length - 1][1]
        const [newPartner, error] = await Partner.getPartner(
            partner.name,
            partner.email,
            partner.id
        )

        if (error.code) {
            showError(error.message)
            return
        }
        updatePartner(newPartner)
    }

    // set the logged state if needed, without blocking the rendering
    React.useEffect(() => {
        loadEmailContacts()
    }, [])

    /**
     * When the task pane is pinned on the desktop app, and that we open a new email.
     */
    function newEmailOpened() {
        email = new Email()
        loadEmailContacts()
    }

    React.useEffect(() => {
        window.addEventListener('newEmailOpened', newEmailOpened)
        return () => {
            window.removeEventListener('newEmailOpened', newEmailOpened)
        }
    }, [])

    return (
        <div className={styles.root}>
            {logged && (
                <div className={styles.header}>
                    <Button
                        disabled={pagesPartner.length <= 1}
                        className={styles.goBack}
                        icon={<ArrowLeftRegular />}
                        title={_t('Go back')}
                        size="small"
                        shape="circular"
                        appearance="subtle"
                        onClick={() => goBack()}
                    />

                    <GlobalLoading />

                    <Menu>
                        <MenuTrigger disableButtonEnhancement>
                            <MenuButton
                                appearance="subtle"
                                icon={<MoreVerticalRegular />}
                                size="medium"
                            />
                        </MenuTrigger>

                        <MenuPopover className={styles.kebab}>
                            <MenuList>
                                <MenuItem
                                    className={styles.kebabButton}
                                    onClick={onRefresh}
                                    disabled={
                                        !pagesPartner.length ||
                                        !pagesPartner[
                                            pagesPartner.length - 1
                                        ][1]
                                    }
                                >
                                    <div>
                                        <span>{_t('Refresh')}</span>
                                        <ArrowClockwiseRegular />
                                    </div>
                                </MenuItem>
                                <MenuItem
                                    className={styles.kebabButton}
                                    onClick={() => logout()}
                                >
                                    <div>
                                        <span>{_t('Log out')}</span>
                                        <SignOutRegular />
                                    </div>
                                </MenuItem>
                            </MenuList>
                        </MenuPopover>
                    </Menu>
                </div>
            )}
            {loading ? <Loading /> : currentPage}
        </div>
    )
}

export default App
