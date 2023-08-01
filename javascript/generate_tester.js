
function do_process() {
    let a = args_to_array(arguments)
    var id = randomId()
    let btn_run = gradioApp().querySelector("#gtt_btn_generate");
    let btn_cancel = gradioApp().querySelector("#gtt_btn_cancel");
    btn_cancel.style.display = "block"
    btn_run.style.display = "none"
    let progressBar = gradioApp().querySelector('#gtt_progress_bar1')
    requestProgress(id, progressBar, null, function () {
        let btn_run = gradioApp().querySelector("#gtt_btn_generate");
        let btn_cancel = gradioApp().querySelector("#gtt_btn_cancel");
        btn_cancel.style.display = "none"
        btn_run.style.display = "block"
        let update_btn = gradioApp().querySelector("#gtt_btn_update")
        update_btn.click()
    })

    // let load_effect = gradioApp().querySelector('#img_reg_preview .wrap')
    //
    // if (load_effect) {
    //     load_effect.style.display = "none"
    // }
    let progressBar2 = gradioApp().querySelector('.progress')
    tt_mutationObserver = tt_mutationObserver || new MutationObserver(function (m) {
        let update_btn = gradioApp().querySelector("#gtt_btn_update")
        update_btn.click()
    })


    tt_mutationObserver.observe(progressBar2, {childList: true, subtree: true})
    a[0] = id
    return a
}