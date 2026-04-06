document.getElementById("login_detail").addEventListener("submit",getDetail);

function getDetail(event){

    // stop the page from refresh, so we can get the login detail
    event.preventDefault();

    //reset the error message
    document.getElementById("email_error").textContent = "";
    document.getElementById("password_error").textContent = "";
     
    // get the user input
    let email = document.getElementById("email").value.trim();
    let password = document.getElementById("password").value.trim();
    

    //console.log(username,password);
    //window.location.replace("/create_account.html")
    if(email === ""){
        document.getElementById("email_error").textContent = "Please enter a Email address"
        return;
    }
    if(password === "" ){
        document.getElementById("password_error").textContent = "Please enter a Password"
        return;
    }
    
    //set to submit first, testing
    document.getElementById("login_detail").submit();
    servervVerifyUserLogin(username,password);
    
}

async function servervVerifyUserLogin(username,password){
    
    try{

        const response = await fetch( /api/,{
            method: "POST",
            headers:{"Content-Type": "application/json"},
            body: JSON.stringify({username, password})
        }); // API needed

        //status code 200, successful in login
        if (response.ok) {
            const data = await response.json();
            console.log("Login success:", data);

            //redirct
            //window.location.replace("/create_account.html");
        }else if (response.status === 400 || response.status === 422){
            document.getElementById("error_code").textContent = "Invalid input";
            return;
        }else if (response.status === 401) {
             document.getElementById("error_code").textContent = "Incorrect Email or Password";
            return;
        }else{
            console.error("Error status code:", response.status)
        }


        
    }catch(error){
        console.error("Network error:", error);
        
    }


}