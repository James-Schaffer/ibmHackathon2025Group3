$(document).ready(function() {
    let loginForm = document.getElementById("login_form");
    let signupForm = document.getElementById("signupForm");

    let username = $("#username").val();
    let password = $("#password").val();
    let symbol = ["£", "*", "$", "&", "!", "%", "^", "#", "-", "+", "_", "=", "|"];
    let digits = ["0", "1", "2", "3", "4", "5", "6", "7", "8", "9"];
    
    //Check if username is valid
    $("#username").keyup(function() {
        if ($(this).val()) {
            username = $(this).val();
            if (username.length <= 2) {
                $("#useraddon1").removeClass("btn-success").addClass("btn-danger");
                $("#username_text").text("Username too short");
                usernameValid = false;
            } else if (username.length > 16) {
                $("#useraddon1").removeClass("btn-success").addClass("btn-danger");
                $("#username_text").text("Username too long");
                usernameValid = false;
            } else {
                $("#useraddon1").removeClass("btn-danger").addClass("btn-success");
                usernameValid = true;
                $("#username_text").text("Valid username.")
            };
        } else {
            $("#useraddon1").removeClass("btn-danger").removeClass("btn-success");
            usernameValid = false;
            $("#username_text").text("Please enter a username.");
        };
    });
    
    $("#password").keyup(function() {
        if ($(this).val()) {
            password = $(this).val();
            if (password.length >= 1) {
                let countsym = 0;
                for (let i in symbol) {
                    if (password.includes(symbol[i])) {
                        countsym += 1;
                    };
                    
                };
                let countdig = 0;
                for (let j in digits) {
                    if (password.includes(j)) {
                        countdig += 1;
                    };
                    
                };
                if (countsym > 0 && countdig > 0) {
                    $("#passaddon1").removeClass("btn-danger").addClass("btn-success");
                    passwordValid = true;
                    $("#password_text").text("Valid password.")
                } else if (countsym <= 0) {
                    $("#passaddon1").removeClass("btn-success").addClass("btn-danger");
                    passwordValid = false;
                    $("#password_text").text("Password missing a symbol, e.g. $, £, or *.");
                } else if (countdig <= 0) {
                    $("#passaddon1").removeClass("btn-success").addClass("btn-danger");
                    passwordValid = false;
                    $("#password_text").text("Password missing a digit, e.g. 0-9");
                };
            } else {
                $("#passaddon1").removeClass("btn-success").addClass("btn-danger");
                passwordValid = false;
                $("#password_text").text("Password too short.");
            };
        } else {
            $("#passaddon1").removeClass("btn-success").removeClass("btn-danger")
            passwordValid = false;
            $("#password_text").text("Enter password.");
        };
    });
    
    if (loginForm) {
        loginForm.addEventListener("submit", (e) => {
            if (usernameValid && passwordValid) {    
                e.preventDefault();
                console.log(`LOGIN - username : ${username} , password : ${password}`);
                //Do login stuff here
                //to to home + set login cookie (see app.js)
                setLoginCookies(username);
                window.location.href = "./homePage.html";
            } else {
                $("#username_text").text("Cannot submit invalid username or password.")
            };
        });
    };

    if (signupForm) {
        signupForm.addEventListener("submit", (e) => {
            if (usernameValid && passwordValid) {    
                e.preventDefault();
                console.log(`SIGNUP - username : ${username} , password : ${password}`);
                //Signup system here

                //to to home + set login cookie (see app.js)
                setLoginCookies(username);
                window.location.href = "./homePage.html";
            } else {
                $("#username_text").text("Cannot submit invalid username or password.")
            };
                
        });
    };
});