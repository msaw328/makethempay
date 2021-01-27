// adds toast with notification text to element with id = toast_container
export function add_toast(notification) {
    let div = document.createElement('div');

    div.className = 'toast';

    div.innerHTML = `
        <div class="toast-header">
            <strong class="me-auto">Notification:</strong>
            <button type="button" class="btn-close" data-bs-dismiss="toast" aria-label="Close"></button>
        </div>
        <div class="toast-body">` +
            notification +
        `</div>
        `;

    document.getElementById('toast_container').appendChild(div);
}

// shows all toasts
export function show_toasts() {
    let toastElList = [].slice.call(document.querySelectorAll('.toast'));
    let toastList = toastElList.map(function(toastEl) {return new bootstrap.Toast(toastEl)});
    toastList.forEach(toast => toast.show());
}

// removes all toasts
export function remove_toasts() {
    let toasts = document.getElementsByClassName('toast');
    while( toasts[0] ) {
        toasts[0].parentNode.removeChild(toasts[0]);
    }
}
