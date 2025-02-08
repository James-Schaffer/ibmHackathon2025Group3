let loginForm = document.getElementById("loginForm");
let signupForm = document.getElementById("signupForm");

if (loginForm) {
loginForm.addEventListener("submit", (e) => {
    e.preventDefault();

    let username = $("#username").val();
    let password = $("#password").val();

    console.log(`LOGIN - username : ${username} , password : ${password}`);

    //LOGIN SYSTEM HERE
});}

if (signupForm) {
signupForm.addEventListener("submit", (e) => {
    e.preventDefault();

    let username = $("#username").val();
    let password = $("#password").val();

    console.log(`SIGNUP - username : ${username} , password : ${password}`);

    //SIGNUP SYSTEM HERE
});}