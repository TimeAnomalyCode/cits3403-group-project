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
    constructor(randomArray, startIndex = 0) {
        if (!Array.isArray(randomArray) || randomArray.length === 0) {
            throw new Error("randomArray must be a non-empty array");
        }

        this.random_array = randomArray;
        this.bufferSize = randomArray.length;
        this.index = startIndex % this.bufferSize;
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
    constructor(callback, args = [], duration = 180) {
        this.duration = duration;
        this.callback = callback;
        this.args = args;
        this.hasStart = false;

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

    start() {
        if (this.hasStart) {
            return this;
        }

        this.endTime = Date.now() + this.duration * 1000;
        this.create();
        this.hasStart = true;

        return this;
    }

    remaining() {
        if (this.endTime === null) {
            return this.duration;
        }

        return Math.max(0, (this.endTime - Date.now()) / 1000);
    }

    clear() {
        if (this.timer !== null) {
            clearTimeout(this.timer);
            this.timer = null;
        }
        this.hasStart = false;
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
    static destroySpecificTile(cell, match_random) {
        const [r, c] = match_random.randomPickNonEmpty(cell);

        if (r === null || c === null) {
            return [cell, false];
        }

        cell[r][c] = 0;
        return [cell, true];
    }

    /**
     * @param {MatchRandom} match_random
     */
    static createRandomTile(cell, match_random) {
        const [r, c] = match_random.randomPickEmpty(cell);

        if (r === null || c === null) {
            return [cell, false];
        }

        cell[r][c] = 2 ** match_random.next_range(1, 7);
        return [cell, true];
    }

    /**
     * @param {MatchRandom} match_random
     */
    static rearrangeBoard(cell, match_random) {
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

        return cell;
    }

    /**
     * @param {MatchRandom} match_random
     */
    static makeRandomNegativeTile(cell, match_random) {
        const [r, c] = match_random.randomPickEmpty(cell);

        if (r === null || c === null) {
            return [cell, false];
        }

        cell[r][c] = -1 * 2 ** match_random.next_range(1, 4);
        return [cell, true];
    }
}

const socket = io();
console.log(socket);

const username = data.username || null;
const match_id = data.match_id || null;

function end_game(text) {
    console.log("Match Ended: ", text);
    console.log(Date.now());
}
