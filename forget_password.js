document.getElementById("update_login_detail").addEventListener("submit",getDetail);

//password requirement
function validateHasLower(password){
  const hasLower = /[a-z]/.test(password);
  return hasLower;
}
function validateHasUpper(password){
  const hasUpper = /[A-Z]/.test(password);
  return hasUpper;
}
function validateHasNumber(password){
 const hasNumber = /\d/.test(password);
 return hasNumber;
}
function validateHasSpecial(password){
  const hasSpecial = /[@$!%*?&]/.test(password);
  return hasSpecial;
}
function validateHasMinLength(password){
  const hasMinLength = password.length >= 8;
  return hasMinLength;
}

function getDetail(e){

    // stop the page from refresh, so we can get the login detail
    e.preventDefault();

    //reset the error message
    document.getElementById("email_error").textContent = "";
    document.getElementById("password_error").textContent = "";
    document.getElementById("confirm_password_error").textContent = "";

    // get the user input
    let email = document.getElementById("email").value.trim();
    let password = document.getElementById("password").value.trim();
    let confirm_password = document.getElementById("confirmPassword").value.trim();
    //console.log(username,password);
    //window.location.replace("/create_account.html")

    //check
    if(email === ""){
        document.getElementById("email_error").innerHTML = "Please enter a Email"
        return;
    }

    if(!validateHasLower(password) ){
        document.getElementById("password_error").innerHTML = "Password must contain a lowercase character"
        return;
    }else if(!validateHasUpper(password)){
        document.getElementById("password_error").innerHTML = "Password must contain a uppercase character"
        return;

    }else if(!validateHasNumber(password)){
        document.getElementById("password_error").innerHTML = "Password must contain a number"
        return;

    }else if(!validateHasSpecial(password)){
        document.getElementById("password_error").innerHTML = "Password must contain a special character"
        return;

    }else if(!validateHasMinLength(password)){
        document.getElementById("password_error").innerHTML = "Password must contain at least 8 character"
        return;
    }

    if(confirm_password !== password ){
        document.getElementById("confirm_password_error").innerHTML = "Comfirm password does not match"
        return;
    }

    document.getElementById("update_login_detail").submit();// this line is just testing for now, mimicing submit(fetch) function
    communciateWithServer(email,password);
    
}

async function communciateWithServer(email,password){
    
    try{

        const response = await fetch( /api/,{
            method: "POST",
            headers:{"Content-Type": "application/json"},
            body: JSON.stringify({email, password})
        }); // API needed

        //successfully in update a registered user information
        if (response.status == 200) {
            const data = await response.json();
            console.log("Password reset successful:", data);

            //redirct
            //window.location.replace("/create_account.html");
        }else if (response.status === 400 || response.status === 422){
            document.getElementById("error_code").textContent = "Invalid input";
        
        }else if (response.status === 404) {
            document.getElementById("error_code").textContent = "User Not Found";
            return;
        
        }else{
            console.error("Error status code:", response.status)
        }


        
    }catch(error){
        console.error("Network error:", error);
        
    }
}
