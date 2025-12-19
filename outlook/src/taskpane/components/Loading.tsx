import { Image, makeStyles } from '@fluentui/react-components'
import React from 'react'
import { _t } from '../../helpers/translate'

export interface LoadingProps {}

const useStyles = makeStyles({
    loading: {
        margin: 'auto',
        display: 'block',
    },
})

const Loading: React.FC<LoadingProps> = (_props: LoadingProps) => {
    const styles = useStyles()

    return (
        <Image
            className={styles.loading}
            width="32px"
            src="assets/spinner.gif"
            alt={_t('Loading')}
        />
    )
}

export default Loading
