// adds alert with message text under the navbar element
export function add_alert(message) {
    let alertsContainer = document.getElementById('alerts-container')
    if (alertsContainer){
        let div = document.createElement('div');

        div.classList.add('alert', 'alert-secondary', 'alert-dismissible', 'fade', 'show', 'sticky-top')

        div.innerHTML = 
                message +
            `<button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>`;

        alertsContainer.appendChild(div);
    } else {
        console.log('No alerts-container on this page!')
    }
}
