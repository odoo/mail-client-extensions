import { Image, makeStyles } from '@fluentui/react-components'
import React from 'react'
import { _t } from '../../helpers/translate'

export interface GlobalLoadingProps {}

const useStyles = makeStyles({
    loading: {
        float: 'right',
    },
})

const GlobalLoading: React.FC<GlobalLoadingProps> = (
    _props: GlobalLoadingProps
) => {
    const styles = useStyles()

    const [visible, setVisible] = React.useState(false)
    const showGlobalLoading = () => {
        setVisible(true)
    }

    const hideGlobalLoading = () => {
        setVisible(false)
    }

    React.useEffect(() => {
        window.addEventListener('showGlobalLoading', showGlobalLoading)
        window.addEventListener('hideGlobalLoading', hideGlobalLoading)
        return () => {
            window.removeEventListener('showGlobalLoading', showGlobalLoading)
            window.removeEventListener('hideGlobalLoading', hideGlobalLoading)
        }
    }, [])

    return (
        visible && (
            <Image
                className={styles.loading}
                width="20px"
                src="assets/spinner.gif"
                alt={_t('Loading')}
            />
        )
    )
}

export const showGlobalLoading = () => {
    const event = new CustomEvent('showGlobalLoading')
    window.dispatchEvent(event)
}

export const hideGlobalLoading = () => {
    const event = new CustomEvent('hideGlobalLoading')
    window.dispatchEvent(event)
}

export default GlobalLoading
