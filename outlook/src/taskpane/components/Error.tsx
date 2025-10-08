import { makeStyles } from '@fluentui/react-components'
import * as React from 'react'

export interface ErrorProps {}

const useStyles = makeStyles({
    container: {
        position: 'absolute',
        zIndex: '999',
        bottom: '0',
        padding: '5px 10px',
        borderRadius: '2px',
        left: '50%',
        transform: 'translate(-50%, -50%)',
        backgroundColor: '#fafafa',
        boxShadow: '0 1px 3px rgba(0,0,0,0.12), 0 1px 2px rgba(0,0,0,0.24)',
        minWidth: '200px',
        textAlign: 'center',
    },
    progress: {
        width: '100%',
        backgroundColor: '#e74c3c',
        height: '2px',
        position: 'absolute',
        left: '0',
        bottom: '0',
        animationName: {
            '0%': { width: '100%' },
            '100%': { width: '0%' },
        },
        animationDuration: '2s',
        animationTimingFunction: 'linear',
    },
})

const Error: React.FC<ErrorProps> = (_props: ErrorProps) => {
    const styles = useStyles()

    const [message, setMessage] = React.useState(null)
    const timeoutRef = React.useRef<NodeJS.Timeout | null>(null)

    const showError = (event) => {
        if (timeoutRef.current) {
            clearTimeout(timeoutRef.current)
        }
        setMessage(null)
        requestAnimationFrame(() => {
            // restart the animation
            setMessage(event.detail.message)
        })
        timeoutRef.current = setTimeout(() => {
            setMessage(null)
            timeoutRef.current = null
        }, 2000)
    }

    React.useEffect(() => {
        window.addEventListener('showError', showError)
        return () => {
            window.removeEventListener('showError', showError)
        }
    }, [])

    if (!message) {
        return null
    }

    return (
        <div className={styles.container}>
            {message}
            <div className={styles.progress} />
        </div>
    )
}

export const showError = (message) => {
    const event = new CustomEvent('showError', { detail: { message } })
    window.dispatchEvent(event)
}

export default Error
