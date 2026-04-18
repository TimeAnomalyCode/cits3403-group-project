document.addEventListener("DOMContentLoaded", () => {

    const profileBtn = document.getElementById("profileBtn");
    const createGameBtn = document.getElementById("createGameBtn");
    const createTournamentBtn = document.getElementById("createTournamentBtn");
    const joinGameBtn = document.getElementById("joinGameBtn");
    const matchCodeInput = document.getElementById("matchCode");

    profileBtn.addEventListener("click", () => {
        window.location.href = "/profile";
    });

    createGameBtn.addEventListener("click", () => {
        window.location.href = "/game";
    });

    createTournamentBtn.addEventListener("click", async () => {
        const res = await fetch("/api/create-tournament", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
                name: "My Tournament",
                players: 8,
                privacy: "private"
            })
        });

        const data = await res.json();

        window.location.href = "/tournament-lobby";
    });

    joinGameBtn.addEventListener("click", async () => {
        const code = matchCodeInput.value.trim();

        if (!/^\d{5}$/.test(code)) {
            alert("Enter valid 5-digit code");
            return;
        }

        const res = await fetch("/api/join-tournament", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ joinCode: code })
        });

        const data = await res.json();

        if (data.error) {
            alert(data.error);
            return;
        }

        window.location.href = "/tournament-lobby";
    });

});