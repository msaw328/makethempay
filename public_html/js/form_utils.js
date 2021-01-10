// converts HTML form into a JS object with values from inputs
export function form_to_obj(form) {
    var formData = new FormData(form)
    var requestData = Object.fromEntries(formData.entries())
    return requestData
}

// performs an async request sending json
// url - where
// method - POST/GET probably
// body - JSON to be sent in POST, ignored if GET
// callback - function, takes response object, executed after fetch is done
export function async_json_request(url, method, body, callback) {
    fetch(url, {
        headers: {
            'Content-Type': 'application/json'
        },
        method: 'POST',
        body: (method == 'POST') ? body : null
    }).then(resp => resp.json()).then(callback)
}
