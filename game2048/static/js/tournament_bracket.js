document.addEventListener("DOMContentLoaded", async () => {

    // Fetch tournament data from API
    let players = [];
    let tournamentName = "Tournament Bracket";

    try {
        const res = await fetch("/api/lobby-state");
        const data = await res.json();

        if (!data.error) {
            players = data.players || [];
            tournamentName = data.name || "Tournament Bracket";
        }
    } catch (err) {
        console.log("Could not fetch API, using example data");
    }

    // Fallback to example data if API fails or returns empty
    if (players.length === 0) {
        players = ["Alice", "Bob", "Charlie", "David", "Eve", "Frank", "Grace", "Henry"];
    }

    const playerCount = players.length;
    const round1El = document.getElementById("round1");
    const round2El = document.getElementById("round2");
    const round3El = document.getElementById("round3");
    const round4El = document.getElementById("round4");
    const championEl = document.getElementById("champion");

    // Update title
    document.querySelector("h2").textContent = tournamentName;

    function createMatch(p1, p2) {
        const div = document.createElement("div");
        div.className = "match";

        div.innerHTML = `
        <div class="player">${p1 || "TBD"}</div>
        <div class="player">${p2 || "TBD"}</div>
    `;

        return div;
    }

    // Dynamic bracket based on player count
    if (playerCount >= 16) {
        // 16-player bracket: RO16 → QF → SF → Final
        const round1Players = players.slice(0, 16);
        const round2Winners = players.slice(0, 8);
        const round3Winners = players.slice(0, 4);
        const round4Winners = players.slice(0, 2);

        // Round 1 (Round of 16)
        for (let i = 0; i < round1Players.length; i += 2) {
            round1El.appendChild(createMatch(round1Players[i], round1Players[i + 1]));
        }

        // Round 2 (Quarterfinals)
        for (let i = 0; i < round2Winners.length; i += 2) {
            round2El.appendChild(createMatch(round2Winners[i], round2Winners[i + 1]));
        }

        // Round 3 (Semifinals)
        for (let i = 0; i < round3Winners.length; i += 2) {
            round3El.appendChild(createMatch(round3Winners[i], round3Winners[i + 1]));
        }

        // Round 4 (Final)
        for (let i = 0; i < round4Winners.length; i += 2) {
            round4El.appendChild(createMatch(round4Winners[i], round4Winners[i + 1]));
        }

        // Update labels
        round1El.parentElement.querySelector(".round-label").textContent = "Round of 16";
        round2El.parentElement.querySelector(".round-label").textContent = "Quarterfinals";
        round3El.parentElement.querySelector(".round-label").textContent = "Semifinals";
        round4El.parentElement.querySelector(".round-label").textContent = "Final";

    } else if (playerCount >= 8) {
        // 8-player bracket: QF → SF → Final
        const round1Players = players.slice(0, 8);
        const round2Winners = players.slice(0, 4);
        const round3Winners = players.slice(0, 2);

        // Round 1 (Quarterfinals)
        for (let i = 0; i < round1Players.length; i += 2) {
            round1El.appendChild(createMatch(round1Players[i], round1Players[i + 1]));
        }

        // Round 2 (Semifinals)
        for (let i = 0; i < round2Winners.length; i += 2) {
            round2El.appendChild(createMatch(round2Winners[i], round2Winners[i + 1]));
        }

        // Round 3 (Final)
        for (let i = 0; i < round3Winners.length; i += 2) {
            round3El.appendChild(createMatch(round3Winners[i], round3Winners[i + 1]));
        }

        // Update labels
        round1El.parentElement.querySelector(".round-label").textContent = "Quarterfinals";
        round2El.parentElement.querySelector(".round-label").textContent = "Semifinals";
        round3El.parentElement.querySelector(".round-label").textContent = "Final";
        round4El.parentElement.style.display = "none";

    } else if (playerCount >= 4) {
        // 4-player bracket: SF → Final
        const round1Players = players.slice(0, 4);
        const round2Winners = players.slice(0, 2);

        // Round 1 (Semifinals)
        for (let i = 0; i < round1Players.length; i += 2) {
            round1El.appendChild(createMatch(round1Players[i], round1Players[i + 1]));
        }

        // Round 2 (Final)
        for (let i = 0; i < round2Winners.length; i += 2) {
            round2El.appendChild(createMatch(round2Winners[i], round2Winners[i + 1]));
        }

        // Update labels
        round1El.parentElement.querySelector(".round-label").textContent = "Semifinals";
        round2El.parentElement.querySelector(".round-label").textContent = "Final";
        round3El.parentElement.style.display = "none";
        round4El.parentElement.style.display = "none";

    } else if (playerCount >= 2) {
        // 2-player bracket: Final only
        for (let i = 0; i < playerCount; i += 2) {
            round1El.appendChild(createMatch(players[i], players[i + 1]));
        }

        round1El.parentElement.querySelector(".round-label").textContent = "Final";
        round2El.parentElement.style.display = "none";
        round3El.parentElement.style.display = "none";
        round4El.parentElement.style.display = "none";
    }

    // Champion
    championEl.textContent = "🏆 Champion: TBD";

    // Draw connecting lines
    drawBracketLines();
    window.addEventListener("resize", drawBracketLines);
});

function drawBracketLines() {
    const svg = document.getElementById("bracket-lines");
    const container = document.querySelector(".bracket-container");

    if (!svg || !container) return;

    svg.setAttribute("width", container.scrollWidth);
    svg.setAttribute("height", container.scrollHeight);
    svg.innerHTML = "";

    const lineColor = "#d0d0d0";
    const lineWidth = 1.5;

    function getMatchCenterY(match) {
        const rect = match.getBoundingClientRect();
        const containerRect = container.getBoundingClientRect();
        return rect.top - containerRect.top + rect.height / 2 + container.scrollTop;
    }

    function getMatchX(match) {
        const rect = match.getBoundingClientRect();
        const containerRect = container.getBoundingClientRect();
        return rect.right - containerRect.left + container.scrollLeft;
    }

    const allRounds = document.querySelectorAll(".round");

    // Connect each round to the next
    for (let roundIdx = 0; roundIdx < allRounds.length - 1; roundIdx++) {
        const currentRoundEl = allRounds[roundIdx];
        const nextRoundEl = allRounds[roundIdx + 1];

        if (!currentRoundEl.offsetParent || !nextRoundEl.offsetParent) continue; // Skip hidden rounds

        const currentMatches = currentRoundEl.querySelectorAll(".match");
        const nextMatches = nextRoundEl.querySelectorAll(".match");

        currentMatches.forEach((match, idx) => {
            const pairIdx = Math.floor(idx / 2);
            if (pairIdx < nextMatches.length) {
                const y1 = getMatchCenterY(match);
                const x1 = getMatchX(match);
                const y2 = getMatchCenterY(nextMatches[pairIdx]);
                const x2 = getMatchX(nextMatches[pairIdx]);

                drawConnectionLine(svg, x1, y1, x2, y2, lineColor, lineWidth);
            }
        });
    }
}

function drawConnectionLine(svg, x1, y1, x2, y2, color, width) {
    const midX = (x1 + x2) / 2;
    const path = document.createElementNS("http://www.w3.org/2000/svg", "path");
    path.setAttribute(
        "d",
        `M ${x1} ${y1} L ${midX} ${y1} L ${midX} ${y2} L ${x2} ${y2}`
    );
    path.setAttribute("stroke", color);
    path.setAttribute("stroke-width", width);
    path.setAttribute("fill", "none");
    path.setAttribute("stroke-linecap", "round");
    svg.appendChild(path);
}
