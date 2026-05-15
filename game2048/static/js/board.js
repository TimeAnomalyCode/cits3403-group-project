/**
 * @typedef {Object} TypeMatch
 * @property {Object.<string, string>} sids
 * @property {string} host
 * @property {string | null} opponent
 * @property {MatchStatus} status
 * @property {string | null} winner
 * @property {string | null} loser
 * @property {Object.<string, any[]>} cells
 * @property {Object.<string, number>} score
 * @property {Object.<string, number>} hidden_score
 * @property {Object.<string, number>} trash_point
 * @property {Object.<string, boolean>} dead
 * @property {any[]} random_array
 * @property {Object.<string, number>} random_array_index
 * @property {number} timer
 * @property {Object.<string, string | null>} is_attacked
 */

/**
 * @typedef {Object} TypeSounds
 * @property {string} credit
 * @property {string} link
 * @property {Howl} howl
 */

const MATCH_STATUS = {
    PENDING: "pending",
    START: "start",
    ONGOING: "ongoing",
    END: "end",
};

class MatchRandom {
    constructor() {
        this.random_array = [];
        this.bufferSize = 0;
        this.index = 0;
    }

    setup(random_array, start_index) {
        if (!Array.isArray(random_array) || random_array.length === 0) {
            throw new Error("randomArray must be a non-empty array");
        }

        if (this.random_array.length === 0) {
            this.random_array = random_array;
            this.bufferSize = random_array.length;
        }

        this.index = start_index % this.bufferSize;
    }

    get_array() {
        return this.random_array;
    }

    get_index() {
        return this.index;
    }

    _next_random() {
        const value = this.random_array[this.index];
        this.index = (this.index + 1) % this.bufferSize;
        return value;
    }

    next_int() {
        return Math.floor(this._next_random() * (2 ** 31 - 1));
    }

    next_float() {
        return this._next_random();
    }

    next_range(start, end) {
        if (start >= end) {
            throw new Error("start must be less than end");
        }

        const rangeSize = end - start;
        return start + Math.floor(this._next_random() * rangeSize);
    }

    choice(array) {
        if (!array || array.length === 0) {
            throw new Error("Cannot choose from an empty array");
        }
        return array[this.next_range(0, array.length)];
    }

    randomPickEmpty(cell) {
        const N = cell.length;
        const emptySpace = [];

        for (let r = 0; r < N; r++) {
            for (let c = 0; c < N; c++) {
                if (cell[r][c] === 0) {
                    emptySpace.push([r, c]);
                }
            }
        }

        if (emptySpace.length === 0) {
            return [null, null];
        }

        const pick = this.next_range(0, emptySpace.length);
        const [r, c] = emptySpace[pick];
        console.log([r, c]);
        return [r, c];
    }

    randomPickNonEmpty(cell) {
        const N = cell.length;
        const nonEmptySpace = [];

        for (let r = 0; r < N; r++) {
            for (let c = 0; c < N; c++) {
                if (cell[r][c] > 0) {
                    nonEmptySpace.push([r, c]);
                }
            }
        }

        if (nonEmptySpace.length === 0) {
            return [null, null];
        }

        const pick = this.next_range(0, nonEmptySpace.length);
        const [r, c] = nonEmptySpace[pick];
        console.log([r, c]);
        return [r, c];
    }

    fisher_yates_shuffle(array) {
        for (let i = array.length - 1; i > 0; i--) {
            const j = this.next_range(0, i + 1);
            [array[i], array[j]] = [array[j], array[i]];
        }
        return array;
    }
}

class MatchTimer {
    constructor(callback, args = []) {
        this.duration = 180;
        this.callback = callback;
        this.args = args;

        this.timer = null;
        this.endTime = null;
    }

    create() {
        if (this.timer !== null) {
            return this;
        }

        this.timer = setTimeout(() => {
            this.callback(...this.args);
        }, this.duration * 1000);

        return this;
    }

    start(duration) {
        if (this.timer !== null) {
            return this;
        }

        this.duration = duration;
        this.endTime = Date.now() + this.duration * 1000;
        this.create();
        return this;
    }

    update(seconds_left) {
        const currentRemaining = this.remaining();

        // If timer is not running
        if (this.timer === null) {
            this.start(seconds_left);
            return this;
        }

        // Only resync if the difference is meaningful
        if (Math.abs(currentRemaining - seconds_left) <= 2) {
            return this;
        }

        this.clear();
        this.duration = seconds_left;
        this.start(seconds_left);

        return this;
    }

    remaining() {
        if (this.endTime === null) {
            return this.duration;
        }

        return Math.ceil(Math.max(0, (this.endTime - Date.now()) / 1000));
    }

    clear() {
        if (this.timer !== null) {
            clearTimeout(this.timer);
            this.timer = null;
        }
        this.endTime = null;
        return this;
    }
}

class BoardLogic {
    static compress(row) {
        const newRow = [];
        for (const i of row) {
            if (i !== 0) {
                newRow.push(i);
            }
        }
        return newRow;
    }

    static merge(row) {
        let score = 0;

        for (let i = 0; i < row.length - 1; i++) {
            if (row[i] === row[i + 1]) {
                row[i] = row[i] * 2;
                row[i + 1] = 0;
                score += row[i];
            } else if (row[i] < 0 || row[i + 1] < 0) {
                const s = row[i] + row[i + 1];
                if (s === 0) {
                    row[i] = 0;
                    row[i + 1] = 0;
                }
            }
        }

        return [row, score];
    }

    static left(cell) {
        const newCell = [];
        let totalScoreForMove = 0;
        let moved = false;

        for (const r of cell) {
            let row = BoardLogic.compress(r);
            [row, totalScoreForMove] = [
                BoardLogic.merge(row)[0],
                totalScoreForMove,
            ];

            const mergeResult = BoardLogic.merge(row);
            row = mergeResult[0];
            const score = mergeResult[1];

            row = BoardLogic.compress(row);

            const length = r.length - row.length;

            for (let i = 0; i < length; i++) {
                row.push(0);
            }

            if (JSON.stringify(row) !== JSON.stringify(r)) {
                moved = true;
            }

            newCell.push(row);
            totalScoreForMove += score;
        }

        return [newCell, moved, totalScoreForMove];
    }

    static right(cell) {
        const reverseCell = [];
        const tempCell = [];

        for (const i of cell) {
            reverseCell.push([...i].reverse());
        }

        const [newCell, moved, totalScoreForMove] =
            BoardLogic.left(reverseCell);

        for (const r of newCell) {
            tempCell.push([...r].reverse());
        }

        return [tempCell, moved, totalScoreForMove];
    }

    static transform(cell) {
        const newCell = [];

        for (let c = 0; c < cell.length; c++) {
            const newArray = [];
            for (const r of cell) {
                newArray.push(r[c]);
            }
            newCell.push(newArray);
        }

        return newCell;
    }

    static up(cell) {
        let totalScoreForMove = 0;
        let moved = false;

        cell = BoardLogic.transform(cell);
        const cell2 = [];

        for (const c of cell) {
            let column = BoardLogic.compress(c);
            const mergeResult = BoardLogic.merge(column);
            column = mergeResult[0];
            const score = mergeResult[1];

            column = BoardLogic.compress(column);

            const length = c.length - column.length;

            for (let i = 0; i < length; i++) {
                column.push(0);
            }

            if (JSON.stringify(c) !== JSON.stringify(column)) {
                moved = true;
            }

            cell2.push(column);
            totalScoreForMove += score;
        }

        const newCell = BoardLogic.transform(cell2);
        return [newCell, moved, totalScoreForMove];
    }

    static down(cell) {
        let totalScoreForMove = 0;
        let moved = false;

        cell = BoardLogic.transform(cell);
        console.log(cell);

        const cell2 = [];

        for (let c of cell) {
            c = [...c].reverse();

            let column = BoardLogic.compress(c);
            const mergeResult = BoardLogic.merge(column);
            column = mergeResult[0];
            const score = mergeResult[1];

            column = BoardLogic.compress(column);

            const length = c.length - column.length;

            for (let i = 0; i < length; i++) {
                column.push(0);
            }

            if (JSON.stringify(c) !== JSON.stringify(column)) {
                moved = true;
            }

            column = column.reverse();
            cell2.push(column);
            totalScoreForMove += score;
        }

        const newCell = BoardLogic.transform(cell2);
        return [newCell, moved, totalScoreForMove];
    }

    static hasMove(cell) {
        const N = cell.length;

        for (let r = 0; r < N; r++) {
            for (let c = 0; c < N; c++) {
                if (cell[r][c] === 0) {
                    return true;
                }
                if (c < N - 1 && cell[r][c] === cell[r][c + 1]) {
                    return true;
                }
                if (r < N - 1 && cell[r][c] === cell[r + 1][c]) {
                    return true;
                }
                if (c < N - 1 && cell[r][c] + cell[r][c + 1] <= 0) {
                    return true;
                }
                if (r < N - 1 && cell[r][c] + cell[r + 1][c] <= 0) {
                    return true;
                }
            }
        }

        return false;
    }
}

class BoardAction {
    /**
     * @param {MatchRandom} match_random
     */
    static spawnTile(cell, match_random) {
        const [r, c] = match_random.randomPickEmpty(cell);

        if (r === null || c === null) {
            return cell;
        }

        const probability = match_random.next_float();
        cell[r][c] = probability < 0.9 ? 2 : 4;

        return cell;
    }

    /**
     * @param {MatchRandom} match_random
     */
    static destroySpecificTile(cell, trash_point, match_random, cost = 4) {
        if (trash_point < cost) {
            return [cell, 0];
        }

        const [r, c] = match_random.randomPickNonEmpty(cell);

        if (r === null || c === null) {
            return [cell, 0];
        }

        cell[r][c] = 0;
        return [cell, cost];
    }

    /**
     * @param {MatchRandom} match_random
     */
    static createRandomTile(cell, trash_point, match_random, cost = 1) {
        if (trash_point < cost) {
            return [cell, 0];
        }

        const [r, c] = match_random.randomPickEmpty(cell);

        if (r === null || c === null) {
            return [cell, 0];
        }

        cell[r][c] = 2 ** match_random.next_range(1, 7);
        return [cell, cost];
    }

    /**
     * @param {MatchRandom} match_random
     */
    static rearrangeBoard(cell, trash_point, match_random, cost = 4) {
        if (trash_point < cost) {
            return [cell, 0];
        }

        const N = cell.length;
        const values = [];

        for (let r = 0; r < N; r++) {
            for (let c = 0; c < N; c++) {
                if (cell[r][c] > 0) {
                    values.push(cell[r][c]);
                    cell[r][c] = 0;
                }
            }
        }

        match_random.fisher_yates_shuffle(values);

        let empty = [];
        for (let r = 0; r < N; r++) {
            for (let c = 0; c < N; c++) {
                if (cell[r][c] === 0) {
                    empty.push([r, c]);
                }
            }
        }

        empty = match_random.fisher_yates_shuffle(empty);

        for (let i = 0; i < values.length; i++) {
            const [r, c] = empty[i];
            cell[r][c] = values[i];
        }

        return [cell, cost];
    }

    /**
     * @param {MatchRandom} match_random
     */
    static makeRandomNegativeTile(cell, trash_point, match_random, cost = 2) {
        if (trash_point < cost) {
            return [cell, 0];
        }

        const [r, c] = match_random.randomPickEmpty(cell);

        if (r === null || c === null) {
            return [cell, 0];
        }

        cell[r][c] = -1 * 2 ** match_random.next_range(1, 4);
        return [cell, cost];
    }
}

const moveMap = {
    ArrowUp: "up",
    ArrowDown: "down",
    ArrowLeft: "left",
    ArrowRight: "right",
    w: "up",
    a: "left",
    s: "down",
    d: "right",
};
const attackMap = {
    i: "destroySpecificTile",
    j: "createRandomTile",
    k: "rearrangeBoard",
    l: "makeRandomNegativeTile",
};
const attackLabels = {
    destroySpecificTile: "Destroy Specific Tile",
    createRandomTile: "Create Random Tile",
    rearrangeBoard: "Rearrange Board",
    makeRandomNegativeTile: "Make Random Negative Tile",
};
// cSpell:disable
/** @type {TypeSounds} */
const sounds = {
    soundtrack: {
        credit: "joshuuu - 41 Short, Loopable Background Music Files",
        link: "https://joshuuu.itch.io/short-loopable-background-music",
        howl: new Howl({
            src: ["/static/audio/Temple.wav"],
            loop: true,
            volume: 0.3,
        }),
    },
    hurt: {
        credit: "jsfxr",
        link: "https://sfxr.me/",
        howl: new Howl({
            src: ["/static/audio/explosion.wav"],
        }),
    },
    attack: {
        credit: "jsfxr",
        link: "https://sfxr.me/",
        howl: new Howl({
            src: ["/static/audio/power_up.wav"],
        }),
    },
    slide_tile: {
        credit: "AardsReal",
        link: "https://freesound.org/people/AardsReal/sounds/842183/",
        howl: new Howl({
            src: ["/static/audio/page_turn.wav"],
        }),
    },
    trash_point: {
        credit: "jsfxr",
        link: "https://sfxr.me/",
        howl: new Howl({
            src: ["/static/audio/pickup_coin.wav"],
        }),
    },
    game_over: {
        credit: "Mountain_Man",
        link: "https://freesound.org/people/Mountain_Man/sounds/382310/",
        howl: new Howl({
            src: ["/static/audio/game_over.wav"],
        }),
    },
};
let isMuted = true;
// cSpell:enable
const match_random = new MatchRandom();
const match_timer = new MatchTimer(end_game, ["random Test"]);
const timerEl = document.getElementById("timer1");
const timerBox = document.getElementById("timerBox");
const layer1 = document.getElementById("layer1");
const layer2 = document.getElementById("layer2");
const board1 = document.getElementById("board1");
const board2 = document.getElementById("board2");
const player_1_score = document.getElementById("player_1_score");
const player_1_trash_point = document.getElementById("player_1_trash_point");
const player_2_score = document.getElementById("player_2_score");
const player_2_trash_point = document.getElementById("player_2_trash_point");
const attack_info1 = document.getElementById("attack_info1");
const attack_info2 = document.getElementById("attack_info2");
const playerDeadIndicator = document.getElementById("is_player_dead");
const opponentDeadIndicator = document.getElementById("is_opponent_dead");
const badge = document.getElementById("resultBadge");
const title = document.getElementById("resultTitle");
const scoreEl = document.getElementById("finalScore");
const creditArea = document.getElementById("creditArea");
const username = data.username;
const match_id = data.match_id;
let opponent_username = "";
let lastAttackId = null;
/** @type {TypeMatch} */
let client_match = {};
let isCountingDown = false;
const N = 4;

function updateTimerDisplay() {
    const remaining = match_timer.remaining();
    timerEl.innerText = remaining;
    timerBox.classList.toggle("text-danger", remaining < 31);
}

function formatAttackLabel(attackId) {
    if (!attackId) {
        return "";
    }

    return attackLabels[attackId] || attackId;
}

function flashAttackInfo1() {
    attack_info1.classList.remove("attack-flash");
    void attack_info1.offsetWidth;
    attack_info1.classList.add("attack-flash");

    setTimeout(() => {
        attack_info1.classList.remove("attack-flash");
    }, 2000);
}
function flashAttackInfo2() {
    attack_info2.classList.remove("attack-flash");
    void attack_info2.offsetWidth;
    attack_info2.classList.add("attack-flash");

    setTimeout(() => {
        attack_info2.classList.remove("attack-flash");
    }, 2000);
}

document.getElementById("start_game").addEventListener("click", () => {
    socket.emit("start_game", match_id);
    if (!sounds.soundtrack.howl.playing() && !isMuted) {
        sounds.soundtrack.howl.play();
    }
});

document.getElementById("muteBtn").addEventListener("click", () => {
    isMuted = !isMuted;

    Howler.mute(isMuted);
    if (!sounds.soundtrack.howl.playing() && !isMuted) {
        sounds.soundtrack.howl.play();
    }

    if (isMuted) {
        muteBtn.classList.remove("btn-outline-secondary");
        muteBtn.classList.add("btn-danger");
        muteBtn.innerHTML = '<i class="bi bi-volume-mute"></i> Muted';
    } else {
        muteBtn.classList.remove("btn-danger");
        muteBtn.classList.add("btn-outline-secondary");
        muteBtn.innerHTML = '<i class="bi bi-volume-up"></i> Sound On';
    }
});

// Update timer display every 250ms to ensure it's responsive
updateTimerDisplay();
setInterval(() => {
    updateTimerDisplay();
}, 250);

const socket = io({
    auth: {
        match_id: match_id,
    },
});

socket.on("countdown_start", (payload = {}) => {
    runCountdownAnimation(() => {}, payload.seconds || 3);
});

socket.on("game_state", (match) => {
    console.log(match);
    // Timer always updates so better to just load from server
    client_match = match;

    if (!opponent_username) {
        opponent_username =
            client_match.host !== username
                ? client_match.host
                : client_match.opponent;
        setOpponentName();
    }

    match_random.setup(
        client_match.random_array,
        client_match.random_array_index[username],
    );

    if (client_match.is_attacked[username]) {
        console.log(`You were attacked with ${client_match.is_attacked[username]}!`);
    }

    if (client_match.status === MATCH_STATUS.PENDING) {
        disableMovement();
    } else if (client_match.status === MATCH_STATUS.START) {
        match_timer.start(client_match.timer);
        renderPlayer();
        renderOpponent();
        if (client_match.dead[username]) {
            disableMovement();
        } else {
            enableMovement();
        }
    } else if (client_match.status === MATCH_STATUS.ONGOING) {
        match_timer.update(client_match.timer);
        renderPlayer();
        renderOpponent();
        if (client_match.dead[username]) {
            disableMovement();
            console.log(`${username} is Dead`);
        } else {
            enableMovement();
        }
    } else if (client_match.status === MATCH_STATUS.END) {
        match_timer.update(0);
        playSFX(sounds.game_over.howl);
        sounds.soundtrack.howl.pause();
        renderPlayer();
        renderOpponent();
        disableMovement();
    }
});

function handleMovement(e) {
    const direction = moveMap[e.key];
    const attack = attackMap[e.key];
    let moved = false;
    let score = 0;
    let cost = 0;
    e.preventDefault();

    if (direction) {
        if (direction === "left") {
            [client_match["cells"][username], moved, score] = BoardLogic.left(
                client_match["cells"][username],
            );
        } else if (direction === "right") {
            [client_match["cells"][username], moved, score] = BoardLogic.right(
                client_match["cells"][username],
            );
        } else if (direction === "up") {
            [client_match["cells"][username], moved, score] = BoardLogic.up(
                client_match["cells"][username],
            );
        } else if (direction === "down") {
            [client_match["cells"][username], moved, score] = BoardLogic.down(
                client_match["cells"][username],
            );
        }

        playSFX(sounds.slide_tile.howl);
        BoardAction.spawnTile(client_match["cells"][username], match_random);

        client_match["score"][username] += score;
        client_match["hidden_score"][username] += score;
        if (client_match["hidden_score"][username] > 128) {
            client_match["trash_point"][username] += 1;
            client_match["hidden_score"][username] -= 128;
            playSFX(sounds.trash_point.howl);
        }
        if (!BoardLogic.hasMove(client_match["cells"][username])) {
            client_match["dead"][username] = true;
            playSFX(sounds.hurt.howl);
        }

        renderPlayer();

        socket.emit("game_state", {
            type: "move",
            match_id: match_id,
            direction: direction,
        });
    }

    if (client_match.dead[opponent_username]) {
        console.log("Your opponent has died!");

        flashAttackInfo1();
        attack_info1.textContent = "Opponent was dead, you can't attack now";

    }

    // If opponent is dead, you can't attack them
    if (
        attack &&
        client_match.trash_point[username] > 0 &&
        !client_match.dead[opponent_username]
    ) {
        if (attack === "destroySpecificTile") {
            [client_match["cells"][opponent_username], cost] =
                BoardAction.destroySpecificTile(
                    client_match["cells"][opponent_username],
                    client_match["trash_point"][username],
                    match_random,
                );
        } else if (attack === "createRandomTile") {
            [client_match["cells"][opponent_username], cost] =
                BoardAction.createRandomTile(
                    client_match["cells"][opponent_username],
                    client_match["trash_point"][username],
                    match_random,
                );
        } else if (attack === "rearrangeBoard") {
            [client_match["cells"][opponent_username], cost] =
                BoardAction.rearrangeBoard(
                    client_match["cells"][opponent_username],
                    client_match["trash_point"][username],
                    match_random,
                );
        } else if (attack === "makeRandomNegativeTile") {
            [client_match["cells"][opponent_username], cost] =
                BoardAction.makeRandomNegativeTile(
                    client_match["cells"][opponent_username],
                    client_match["trash_point"][username],
                    match_random,
                );
        }

        if (cost > 0) {
            playSFX(sounds.attack.howl);
            client_match["trash_point"][username] -= cost;
            socket.emit("game_state", {
                type: "attack",
                match_id: match_id,
                attack_id: attack,
            });
        }
    }
}

function enableMovement() {
    document.addEventListener("keydown", handleMovement);
}

function disableMovement() {
    document.removeEventListener("keydown", handleMovement);
}

function setOpponentName() {
    document.getElementById("opponent_username").innerText =
        opponent_username || "Waiting for player...";
}

function end_game(text) {
    console.log("Match Ended: ", text);
    console.log(Date.now());
    client_match.status = MATCH_STATUS.END;

    let isWin = false;
    const score = client_match.score[username];
    const opponent_score = client_match.score[opponent_username];
    if (score > opponent_score) {
        isWin = true;
    }

    showGameOver(isWin, score);
}

function showGameOver(isWin, score) {
    scoreEl.textContent = score;

    if (isWin) {
        badge.textContent = "Victory";
        badge.className = "badge bg-success mb-3 px-3 py-2";

        title.textContent = "You Won!";
        title.classList.remove("text-danger");
        title.classList.add("text-success");
    } else {
        badge.textContent = "Game Over";
        badge.className = "badge bg-danger mb-3 px-3 py-2";

        title.textContent = "You Lost";
        title.classList.remove("text-success");
        title.classList.add("text-danger");
    }

    document.getElementById("gameOverOverlay").classList.remove("d-none");
}

function renderPlayer() {
    player_1_score.textContent = client_match.score[username];
    // console.log("SCORE: ", client_match.score[username]);
    player_1_trash_point.textContent = client_match.trash_point[username];
    if (client_match.is_attacked[username]) {
        const attackId = client_match.is_attacked[username];
        attack_info1.textContent = `You were attacked with ${formatAttackLabel(attackId)}`;
        flashAttackInfo1();
    }
    render(layer1, board1, client_match.cells[username]);
    updateScores(client_match.score[username], client_match.score[opponent_username]);
    renderDeadIndicators();
}

function renderOpponent() {
    player_2_score.textContent = client_match.score[opponent_username];
    player_2_trash_point.textContent =
        client_match.trash_point[opponent_username];
    if (client_match.is_attacked[opponent_username]) {
        const attackId = client_match.is_attacked[opponent_username];
        attack_info2.textContent = `You are attacking opponent with ${formatAttackLabel(attackId)}`;
        flashAttackInfo2();
    }
    render(layer2, board2, client_match.cells[opponent_username]);
    renderDeadIndicators();
}

function renderDeadIndicators() {
    if (!client_match.dead) {
        return;
    }

    playerDeadIndicator.textContent = client_match.dead[username] ? "💀" : "";
    opponentDeadIndicator.textContent =
        opponent_username && client_match.dead[opponent_username] ? "💀" : "";
    
    if ( client_match.dead[opponent_username]) {
        attack_info1.textContent = "Opponent was dead, you can't attack now";
    } else if (client_match.dead[username]) {
        attack_info1.textContent = "You are dead, you can't attack now";
    }
}

function getTileStyle(value) {
    const tileStyles = {
        2: { background: "#eee4da", color: "#776e65" },
        4: { background: "#ded0b6", color: "#776e65" },
        8: { background: "#f2b179", color: "#f9f6f2" },
        16: { background: "#f59563", color: "#f9f6f2" },
        32: { background: "#f67c5f", color: "#f9f6f2" },
        64: { background: "#f65e3b", color: "#f9f6f2" },
        128: { background: "#edcf72", color: "#f9f6f2" },
        256: { background: "#edcc61", color: "#f9f6f2" },
        512: { background: "#edc850", color: "#f9f6f2" },
        1024: { background: "#edc53f", color: "#f9f6f2" },
        2048: { background: "#edc22e", color: "#f9f6f2" },
        4096: { background: "#3c3a32", color: "#f9f6f2" },
    };

    if (value < 0) {
        return { background: "#8fd4dc", color: "#ffffff" };
    }

    return tileStyles[value] || { background: "#8f7a66", color: "#f9f6f2" };
}

function render(layerEl, boardEl, cell) {
    layerEl.innerHTML = "";

    for (let r = 0; r < N; r++) {
        for (let c = 0; c < N; c++) {
            const v = cell[r][c];

            //skip the coming loop if the value is falsely
            if (!v) {
                continue;
            }

            const g = cellGeometry(boardEl, r, c);

            //making new block in web page
            const el = document.createElement("div");
            const tileStyle = getTileStyle(v);
            el.className =
                "position-absolute fw-bold fs-3 d-flex justify-content-center align-items-center rounded";
            el.textContent = v;

            el.style.width = g.w + "px";
            el.style.height = g.h + "px";
            el.style.top = g.top + "px";
            el.style.left = g.left + "px";
            el.style.backgroundColor = tileStyle.background;
            el.style.color = tileStyle.color;

            layerEl.appendChild(el);
        }
    }
}

function cellGeometry(boardEl, r, c) {
    const cells = boardEl.querySelectorAll(".col-3 > div");
    const el = cells[r * N + c];
    const eR = el.getBoundingClientRect();
    const bR = boardEl.getBoundingClientRect();

    return {
        top: eR.top - bR.top,
        left: eR.left - bR.left,
        w: eR.width,
        h: eR.height,
    };
}

function renderSoundCredits() {
    const uniqueCredits = new Map();

    for (const sound of Object.values(sounds)) {
        if (!uniqueCredits.has(sound.link)) {
            uniqueCredits.set(sound.link, sound.credit);
        }
    }

    // console.log(uniqueCredits);

    const list = document.createElement("ul");
    list.className = "list-group";

    uniqueCredits.forEach((credit, link) => {
        const item = document.createElement("li");
        item.className =
            "list-group-item d-flex justify-content-between align-items-center";

        const text = document.createElement("span");
        text.textContent = credit;

        const anchor = document.createElement("a");
        anchor.href = link;
        anchor.target = "_blank";
        anchor.className = "btn btn-sm btn-outline-primary";
        anchor.textContent = "Source";

        item.appendChild(text);
        item.appendChild(anchor);
        list.appendChild(item);
    });

    const title = document.createElement("h5");
    title.className = "mb-3";
    title.textContent = "Sound Credits";

    creditArea.innerHTML = "";
    creditArea.appendChild(title);
    creditArea.appendChild(list);
}
renderSoundCredits();

// To avoid sound fatigue, the pitch of the SFX will vary
function playSFX(sound, min = 0.9, max = 1.1) {
    if (isMuted) return;
    const id = sound.play();
    const rate = min + Math.random() * (max - min);
    sound.rate(rate, id);
}

// Copy tournament code to clipboard
function copyCode() {
    const code = document.getElementById('match_id').innerText;
    const button = document.getElementById('copyCodeBtn');

    navigator.clipboard.writeText(code).then(() => {
        button.innerText = "Copied!";
        setTimeout(() => {
            button.innerText = "Copy Code";
        }, 1500);
    });

}

// Update the score bars based on the current scores
function updateScores(player_1_score, player_2_score) {
    const p1Bar = document.getElementById("player1-bar");
    const p2Bar = document.getElementById("player2-bar");

    // Initialize widths to 50% each if both scores are zero to avoid division by zero
    let p1Width = 50;
    let p2Width = 50;

    if (player_1_score + player_2_score > 0) {
        p1Width = (player_1_score / (player_1_score + player_2_score)) * 100;
        p2Width = 100 - p1Width;
    }
    // console.log(`Player 1 Score: ${p1Width}, Player 2 Score: ${p2Width}`);

    // Update the widths of the bars
    p1Bar.style.width = p1Width + "%";
    p2Bar.style.width = p2Width + "%";
}

function runCountdownAnimation(onComplete, seconds = 3) {
    const startButton = document.getElementById("start_game");
    const overlay = document.getElementById("countdown-overlay");
    const text = document.getElementById("countdown-text");
    let count = seconds;

    if (!startButton || !overlay || !text) {
        if (onComplete) onComplete();
        return;
    }

    // Disable the start button to prevent multiple clicks during countdown
    startButton.disabled = true;
    startButton.style.visibility = "hidden";

    // Show the overlay and start the countdown
    overlay.classList.remove("d-none");
    text.style.color = "";
    text.innerText = count;
    triggerPop();

    const timer = setInterval(() => {
        count--;

        if (count > 0) {
            text.innerText = count;
            triggerPop();
            return;
        }

        text.innerText = "GO!";
        text.style.color = "#28a745";
        triggerPop();
        clearInterval(timer);

        setTimeout(() => {
            overlay.classList.add("d-none");

            if (onComplete) onComplete();
        }, 350);
    }, 1000);

    function triggerPop() {
        text.classList.remove("countdown-pop");
        void text.offsetWidth;
        text.classList.add("countdown-pop");
    }
}
