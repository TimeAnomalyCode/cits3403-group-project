document.addEventListener("DOMContentLoaded", () => {

    const btn = document.getElementById("createBtn");

    btn.addEventListener("click", async () => {

        const name = document.getElementById("tournamentName").value;
        const players = document.getElementById("playerCount").value;
        const privacy = document.getElementById("privacy").value;

        if (!name) {
            alert("Enter tournament name");
            return;
        }

        const res = await fetch("/api/create-tournament", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
                name,
                players,
                privacy
            })
        });

        const data = await res.json();

        console.log(data);

        window.location.href = "/tournament_lobby";
    });

});