$(document).ready(function() {
    document.documentElement.setAttribute("data-bs-theme", getCookie("theme"));
})

function toggleTheme() {
    let currentTheme = document.documentElement.getAttribute("data-bs-theme");
    let newTheme = currentTheme === "dark" ? "light" : "dark";
    document.documentElement.setAttribute("data-bs-theme", newTheme);

    setCookie("theme", newTheme, 365);
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

function getCookie(name) {
    let cookies = document.cookie.split("; ");
    for (let cookie of cookies) {
        let [cookieName, cookieValue] = cookie.split("=");
        if (cookieName === name) {
            return decodeURIComponent(cookieValue);
        }
    }
    return null;
}
