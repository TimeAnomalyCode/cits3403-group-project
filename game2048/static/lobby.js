document.addEventListener("DOMContentLoaded", () => {
    const nameEl = document.getElementById("tournamentName");
    const codeEl = document.getElementById("codeDisplay");
    const listEl = document.getElementById("playerList");
    const countEl = document.getElementById("playerCount");
    const statusEl = document.getElementById("statusText");
    const startBtn = document.getElementById("startBtn");

    let lobbyData = null;

    async function loadLobby() {
        try {
            const res = await fetch("/api/lobby-state");
            const data = await res.json();

            if (data.error) {
                nameEl.textContent = "No tournament found";
                codeEl.textContent = "—";
                countEl.textContent = "";
                statusEl.textContent = data.error;
                listEl.innerHTML = "";
                startBtn.style.display = "none";
                return;
            }

            lobbyData = data;

            nameEl.textContent = data.name;
            codeEl.textContent = data.code;

            renderPlayers(data);
        } catch (err) {
            console.error("Failed to load lobby:", err);
            statusEl.textContent = "Could not load lobby";
        }
    }

    function renderPlayers(data) {
        listEl.innerHTML = "";

        const currentPlayers = data.players.length;
        const maxPlayers = data.max || currentPlayers;

        countEl.textContent = `${currentPlayers} / ${maxPlayers} players`;

        if (currentPlayers < maxPlayers) {
            statusEl.textContent = "Waiting for players to join...";
        } else {
            statusEl.textContent = "Tournament ready to start";
        }

        data.players.forEach(playerName => {
            const div = document.createElement("div");
            div.className = "player";
            div.textContent = playerName;
            listEl.appendChild(div);
        });

        for (let i = currentPlayers; i < maxPlayers; i++) {
            const div = document.createElement("div");
            div.className = "player empty";
            div.textContent = "Empty Slot";
            listEl.appendChild(div);
        }

        if (currentPlayers >= 2) {
            startBtn.style.display = "inline-block";
        } else {
            startBtn.style.display = "none";
        }
    }

    window.goToProfile = function () {
        window.location.href = "/profile";
    };

    window.copyCode = async function () {
        if (!lobbyData || !lobbyData.code) return;

        try {
            await navigator.clipboard.writeText(lobbyData.code);
            alert("Code copied: " + lobbyData.code);
        } catch (err) {
            alert("Could not copy code");
        }
    };

    window.startTournament = function () {
        window.location.href = "/tournament-bracket";
    };

    loadLobby();
    setInterval(loadLobby, 2000);
});