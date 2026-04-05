function login(event){
    document.getElementById("login_detail").addEventListener("submit",getDetail(event));
}

function getDetail(e){

    // stop the page from refresh, so we can get the login detail
    e.preventDefault();

    //reset the error message
    document.getElementById("email_error").textContent = "";
    document.getElementById("password_error").textContent = "";
    
    // get the user input
    let email = document.getElementById("email").value.trim();
    let password = document.getElementById("password").value.trim();
    //console.log(username,password);
    //window.location.replace("/create_account.html")
    if(email === ""){
        document.getElementById("email_error").innerHTML = "Please enter a Email address"
        return;
    }
    if(password === "" ){
        document.getElementById("password_error").innerHTML = "Please enter a Password"
        return;
    }
    //set to submit first, testing
    document.getElementById("login_detail").submit();
    verifyUserLogin(username,password);
    
}


async function verifyUserLogin(username,password){
    
    try{

        const response = await fetch( /api/,{
            method: "POST",
            headers:{"Content-Type": "application/json"},
            body: JSON.stringify({username, password})
        }); // API needed

        if (response.status === 404) {
            document.getElementById("username_error").innerHTML = "Incorrect Username";
            return;
        }

        if (response.status === 401) {
            document.getElementById("password_error").innerHTML = "Incorrect Password";
            return;
        }

        if (response.ok) {
            const data = await response.json();
            console.log("Login success:", data);

            //redirct
            //window.location.replace("/create_account.html");
        }
    }catch(error){
        console.error("Network error:", error);
        
    }


}