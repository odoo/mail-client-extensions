Office.onReady(() => {
    const params = new URLSearchParams(window.location.search)
    Office.context.ui.messageParent(
        JSON.stringify({
            success: params.get('success'),
            auth_code: params.get('auth_code'),
        })
    )
})
