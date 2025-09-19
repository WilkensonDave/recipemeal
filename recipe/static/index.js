"user strict"

let passwordInput = document.getElementById("password");
let passwordStrength = document.getElementById("passwordstrength");


passwordInput.oninput = function() {
    let passwordValue = passwordInput.value;
    let strRegex = [/[0-9]/, /[a-z]/, /[A-Z]/, /[^0-9a-zA-Z]/];
    let showpasswordStrength = ["1%", "25%", "50%", "75%", "100%"];
    let colors = ["#c1121f", "#e85d04", "#faa307", "#ff9770",  "#008000"];
    count = 0;

    strRegex.forEach((item) =>{
        if(item.test(passwordValue)){
            count += 1;
        }
    });

    if(showpasswordStrength[count] === "1%"){
        passwordStrength.textContent = "";
        passwordStrength.textContent = "weak";

    }else if(showpasswordStrength[count] === "25%"){
        passwordStrength.textContent = "Medium";

    }else if(showpasswordStrength[count] === "50%"){
        passwordStrength.textContent = "Good password";
    }else if(showpasswordStrength[count] === "75%"){
        passwordStrength.textContent = "Strong password";
    }else if(showpasswordStrength[count] === "100%"){
        passwordStrength.textContent = "Very strong password";
    }

    passwordStrength.style.width = showpasswordStrength[count];
    passwordStrength.style.backgroundColor = colors[count];
    
}
