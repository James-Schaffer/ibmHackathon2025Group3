let loginForm = document.getElementById("loginForm");
let signupForm = document.getElementById("signupForm");

if (loginForm) {
loginForm.addEventListener("submit", (e) => {
    e.preventDefault();

    let username = $("#username").val();
    let password = $("#password").val();

    console.log(`LOGIN - username : ${username} , password : ${password}`);

    //validation here

    //LOGIN SYSTEM HERE

    //to to home + set login cookie (see app.js)
    setLoginCookies(username);
    window.location.href = "./index.html";
});}

if (signupForm) {
signupForm.addEventListener("submit", (e) => {
    e.preventDefault();

    let username = $("#username").val();
    let password = $("#password").val();

    console.log(`SIGNUP - username : ${username} , password : ${password}`);

    //validation here

    //SIGNUP SYSTEM HERE

    //to to home + set login cookie (see app.js)
    setLoginCookies(username);
    window.location.href = "./login.html";
});}