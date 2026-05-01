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
const match_random = new MatchRandom();
const match_timer = new MatchTimer(end_game, ["random Test"]);
const timerEl = document.getElementById("timer1");
const layer1 = document.getElementById("layer1");
const layer2 = document.getElementById("layer2");
const board1 = document.getElementById("board1");
const board2 = document.getElementById("board2");
const player_1_score = document.getElementById("player_1_score");
const player_1_trash_point = document.getElementById("player_1_trash_point");
const player_2_score = document.getElementById("player_2_score");
const player_2_trash_point = document.getElementById("player_2_trash_point");
const badge = document.getElementById("resultBadge");
const title = document.getElementById("resultTitle");
const scoreEl = document.getElementById("finalScore");
const username = data.username;
const match_id = data.match_id;
let opponent_username = "";
let client_match = {};
const N = 4;

document.getElementById("start_game").addEventListener("click", () => {
    socket.emit("start_game", match_id);
});

setInterval(() => {
    timerEl.innerText = match_timer.remaining();
}, 250);

const socket = io({
    auth: {
        match_id: match_id,
    },
});

socket.on("game_state", (match) => {
    console.log(match);
    // Timer always updates so better to just load from server
    client_match = match;

    if (!opponent_username) {
        opponent_username =
            match.host !== username ? match.host : match.opponent;
        setOpponentName();
    }

    match_random.setup(match.random_array, match.random_array_index[username]);

    if (match.dead[username]) {
        match_timer.update(match.timer);
        disableMovement();
        renderPlayer();
        renderOpponent();
        return;
    }

    if (match.status === MATCH_STATUS.PENDING) {
        disableMovement();
    } else if (match.status === MATCH_STATUS.START) {
        match_timer.start(match.timer);
        renderPlayer();
        renderOpponent();
        enableMovement();
    } else if (match.status === MATCH_STATUS.ONGOING) {
        match_timer.update(match.timer);
        renderPlayer();
        renderOpponent();
        enableMovement();
    } else if (match.status === MATCH_STATUS.END) {
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

        BoardAction.spawnTile(client_match["cells"][username], match_random);

        client_match["score"][username] += score;
        client_match["hidden_score"][username] += score;
        if (client_match["hidden_score"][username] > 128) {
            client_match["trash_point"][username] += 1;
            client_match["hidden_score"][username] -= 128;
        }
        if (!BoardLogic.hasMove(client_match["cells"][username])) {
            client_match["dead"][username] = true;
        }

        renderPlayer();

        socket.emit("game_state", {
            type: "move",
            match_id: match_id,
            direction: direction,
        });
    }

    if (attack && client_match.trash_point[username] > 0) {
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
    render(layer1, board1, client_match.cells[username]);
}

function renderOpponent() {
    player_2_score.textContent = client_match.score[opponent_username];
    player_2_trash_point.textContent =
        client_match.trash_point[opponent_username];
    render(layer2, board2, client_match.cells[opponent_username]);
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
            el.className =
                "position-absolute bg-warning text-dark fw-bold d-flex justify-content-center align-items-center rounded";
            el.textContent = v;

            el.style.width = g.w + "px";
            el.style.height = g.h + "px";
            el.style.top = g.top + "px";
            el.style.left = g.left + "px";

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
