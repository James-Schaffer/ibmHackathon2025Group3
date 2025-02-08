$(document).ready(function() {
    if (getLoginCookies() == null && !window.location.href.includes("login.html") && !window.location.href.includes("signup.html")) {
        window.location.href = "./login.html";
    }

    console.log(getLoginCookies());
})

function getCookie(name) {
    let nameEQ = name + "=";
    let cookiesArray = document.cookie.split(';');
    for (let i = 0; i < cookiesArray.length; i++) {
        let cookie = cookiesArray[i].trim();
        if (cookie.indexOf(nameEQ) === 0) {
            return decodeURIComponent(cookie.substring(nameEQ.length));
        }
    }
    return null;
}

function setCookie(name, value, days) {
    let expires = "";
    if (days) {
        let date = new Date();
        date.setTime(date.getTime() + (days * 24 * 60 * 60 * 1000)); // Convert days to milliseconds
        expires = "; expires=" + date.toUTCString();
    }
    document.cookie = name + "=" + encodeURIComponent(value) + expires + "; path=/";
}

function setLoginCookies(username) {
    setCookie("username", username, 30);
}

function getLoginCookies() {
    return getCookie("username");
}
