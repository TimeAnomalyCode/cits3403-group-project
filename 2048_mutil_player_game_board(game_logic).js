(function () {
  'use strict';
  
  // 4 x 4
  const N = 4;

  function makeState(boardEl, layerEl, overlayEl, ovIconEl, ovSubEl, scoreEl, trashPointEl) {
    return {
      boardEl, layerEl, overlayEl, ovIconEl, ovSubEl, scoreEl, trashPointEl,
      cells: null,
      score: 0,
      won: false,
      dead: false,
      newR: -1,
      newC: -1,
      hiddenScore: 0,
      trashPoint: 0,
    };
  }

  const State = makeState(
    document.getElementById('board1'),
    document.getElementById('layer1'),
    document.getElementById('overlay1'),
    document.getElementById('ovIcon1'),
    document.getElementById('ovSub1'),
    document.getElementById('player_1_score'),
    document.getElementById('player_1_trash_point')
  );

  document.getElementById('New_game').addEventListener('click', startGame);

  function cellGeometry(s, r, c) {
    const cells = s.boardEl.querySelectorAll('.col-3 > div');
    const el = cells[r * N + c];
    const eR = el.getBoundingClientRect();
    const bR = s.boardEl.getBoundingClientRect();

    return {
      top: eR.top - bR.top,
      left: eR.left - bR.left,
      w: eR.width,
      h: eR.height
    };
  }

  function render(s) {
    s.layerEl.innerHTML = '';

    for (let r = 0; r < N; r++) {
      for (let c = 0; c < N; c++) {
        const v = s.cells[r][c];

        //skip the coming loop if the value is falsely
        if (!v){
          continue;

        }

        const g = cellGeometry(s, r, c);

        //making new block in web page
        const el = document.createElement('div');
        el.className = 'position-absolute bg-warning text-dark fw-bold d-flex justify-content-center align-items-center rounded';
        el.textContent = v;

        el.style.width = g.w + 'px';
        el.style.height = g.h + 'px';
        el.style.top = g.top + 'px';
        el.style.left = g.left + 'px';

        s.layerEl.appendChild(el);
      }
    }

    s.scoreEl.textContent = s.score;
    s.trashPointEl.textContent = s.trashPoint
  }

  function spawnTile(s) {
    const empty = [];

    // look for empty cell
    for (let r = 0; r < N; r++) {
      for (let c = 0; c < N; c++) {
        if (!s.cells[r][c]){
          empty.push([r, c]);
        }
      }
    }

    // full grid no spawn
    if (!empty.length){
      return;
    }

    const [r, c] = empty[Math.floor(Math.random() * empty.length)];
    // inital the game, and adding with random blocks, x < 0.9 -> the'2' block, otherwise the '4' block
    s.cells[r][c] = Math.random() < 0.9 ? 2 : 4;
  }

  function slideLine(line) {
    //it remove 0 from the array, allow later merging as merge should only be merging between 2 element that is next to each other
    const arr = line.filter(v => v !== 0);
    let score = 0;

    // = the merging logic =
    // merging the neighbour element together 
    for (let i = 0; i < arr.length - 1; i++) {
      // if the value of these element is the same
      if (arr[i] === arr[i + 1]) {
        // always left in moving, representation can be adjust uisng reverse
        arr[i] *= 2;
        score += arr[i];
        arr.splice(i + 1, 1); // array.splice(index of remove, number of remove)
      } else if(arr[i] < 0 || arr[i+1] < 0){ //stating the negative tile logic
          let sum = arr[i] + arr[i+1];

          if(sum === 0){
            arr.splice(i, 2);
            i = i - 1; // index shift, becasue the array length change
          }else{
            arr[i] = sum;
            //score = score + arr[i]
            arr.splice(i + 1, 1);
          }
      }
    }
    // if the array have space, append with 0 as placeholder
    while (arr.length < N) arr.push(0);

    return { line: arr, score };
  }
  
  // keyboard control
  function move(s, dir) {
    
    //end the game if dead or win
    if (s.dead || s.won){
      return;
    }
    let moved = false;
    let gained = 0;

    // when block is moving left
    if (dir === 'left') {
      for (let r = 0; r < N; r++) {
        // making a copy for later comparsion
        const orig = s.cells[r].slice();
        const { line, score } = slideLine(orig);

        // check if there is a change, if there is difference in the array, meaning user have moved 
        if (line.join() !== orig.join()) moved = true;

        //update the changed line back to original  
        s.cells[r] = line;
        gained += score;
      }
    }

    // when block is moving right
    if (dir === 'right') {
      for (let r = 0; r < N; r++) {
        // making a copy for later comparsion
        const orig = s.cells[r].slice().reverse();
        const { line, score } = slideLine(orig);

        // check if there is a change, if there is difference in the array, meaning user have moved 
        if (line.join() !== orig.join()) moved = true;
        
        //update the changed line back to original  
        s.cells[r] = line.reverse();
        gained += score;
      }
    }

    // when block is moving up
    if (dir === 'up') {
      for (let c = 0; c < N; c++) {

        // const col = s.cells.map(row => row[c]);

        const col = [];

        for (let r = 0; r < s.cells.length; r++){
          // for each row
          const row = s.cells[r];
          // get the element from a row column   
          const value = row[c];
          // add to column array
          col.push(value);          
        }
        const { line, score } = slideLine(col);

        if (line.join() !== col.join()) moved = true;

        //line.forEach((v, r) => s.cells[r][c] = v);
        //update and write back the cell
        for (let r = 0; r < line.length; r++) {
          const v = line[r];       
          s.cells[r][c] = v;       
        }
        gained += score;
      }
    }

    // when block is moving down
    if (dir === 'down') {
      for (let c = 0; c < N; c++) {
        //const col = s.cells.map(row => row[c]).reverse();
        const col = [];

        for (let r = 0; r < s.cells.length; r++){
          // for each row
          const row = s.cells[r];
          // get the element from a row column   
          const value = row[c];
          // add to column array
          col.push(value);          
        }
        // reverse for down
        col.reverse();
        
        const { line, score } = slideLine(col);

       
        if (line.join() !== col.join()) moved = true;
        //line.reverse().forEach((v, r) => s.cells[r][c] = v);
        // reverse for down
        line.reverse();
        //update and write back the cell
        for (let r = 0; r < line.length; r++) {
          const v = line[r];  
          s.cells[r][c] = v;       
        }
        gained += score;
      }
    }

    if (!moved) return;

    s.score += gained;
    s.hiddenScore = s.hiddenScore + gained;
    // console.log(s.score);
    // console.log(s.hiddenScore);
    
    if(s.hiddenScore > 128){
      s.trashPoint = s.trashPoint + 1;
      s.hiddenScore = s.hiddenScore - 128;
    }

    // spawn blocks after each round
    spawnTile(s);
    // render the block for change
    render(s);

    if (s.cells.some(row => row.includes(2048))) {
      s.won = true;
      showOverlay(s, 'win');
    }

    if (!hasMove(s)) {
      s.dead = true;
      showOverlay(s, 'dead');
    }
  }

  function hasMove(s) {
    // check did the board still have moves 
    for (let r = 0; r < N; r++) {
      for (let c = 0; c < N; c++) {
        if (s.cells[r][c] === 0){
          return true;
        }
        // when the column still have space and the have neighbour block with same number
        if (c < N - 1 && s.cells[r][c] === s.cells[r][c + 1]){
          return true;
        }
        // when the row still have space and the have neighbour block with same number
        if (r < N - 1 && s.cells[r][c] === s.cells[r + 1][c]){
          return true;
        }

        // negative tiles
        if(c < N - 1 && s.cells[r][c] + s.cells[r][c + 1] <= 0){
          return true
        }
        
        if (r < N - 1 && s.cells[r][c] + s.cells[r + 1][c] <= 0){
          return true;
        }

      }
    }
    return false;
  }

  function showOverlay(s, type) {
    s.overlayEl.classList.remove('d-none');

    if (type === 'win') {
      s.ovIconEl.textContent = '2048!';
      s.ovSubEl.textContent = 'You win!';
    } else {
      s.ovIconEl.textContent = 'Game Over';
      s.ovSubEl.textContent = 'No moves left';
    }
  }

  function initState(s) {
    //creating the board
    s.cells = [];

    for (let i = 0; i < N; i++) {
      //make an array 
      const row = Array(N).fill(0);
      // add the array together and forming a full game grid
      s.cells.push(row);
    }

    s.score = 0;
    s.won = false;
    s.dead = false;
    s.trashPoint = 0;
    s.hiddenScore = 0;

    s.overlayEl.classList.add('d-none');

    spawnTile(s);
    spawnTile(s);

    render(s);
  }

  function startGame() {
    initState(State);
  } 

  document.addEventListener('keydown', e => {
    const map = {
      ArrowUp: 'up',
      ArrowDown: 'down',
      ArrowLeft: 'left',
      ArrowRight: 'right',
      w: 'up', a: 'left', s: 'down', d: 'right'
    };

    if (map[e.key]) {
      e.preventDefault();
      move(State, map[e.key]);
    }
  });

  startGame();

  /* == game machine and features == */
  // the following is new game machine that effect on the opponent

  function getRandomInt(min, max) {
    min = Math.ceil(min);
    max = Math.floor(max);
    return Math.floor(Math.random() * (max - min + 1)) + min;
  }

  //random position from board
  function randomPos() {
    const r = Math.floor(Math.random() * N);
    const c = Math.floor(Math.random() * N);
    return [r, c];
  }
  
  // replace a random Tile
  function replaceRandomTile(s, value = null) {
    let full_arry = []
  
    let [r, c] = randomPos();
    full_arry.push([r,c]);
    
     // check for empty board cell
    while(s.cells[r][c] !== 0){
      [r, c] = randomPos(); 
      full_arry.push([r,c]);
      console.log('work');
      if(full_arry.length > 16){
          console.log('full')
          return false
      }
    }
    // check if position is valid
    if (r < 0 || r >= N || c < 0 || c >= N) {
        console.log("Invalid position");
        return false;
      }

    s.cells[r][c] = 2 ** getRandomInt(1, 6)

    return true;
  }

  // remove the specific Tile 
  function destroySpecificTile(s,r,c){
    s.cells[r][c] = 0;
  }

  // rearrange opponents board
  function rearrangeBoard(s){
    
    const values = []

    // take all the value out and make the board all 0
    for(let r = 0; r < N; r++){
      for(let c = 0; c < N; c++){
        if(s.cells[r][c]){
          values.push(s.cells[r][c]);
          s.cells[r][c] = 0;
        }
      }
    }

    //random sort, The Fisher Yates Method
    for(let i = values.length-1; i > 0; i = i - 1){
      let j = Math.floor(Math.random() * (i+1));
      [values[i], values[j]]= [values[j], values[i]];
    }

    // look for empty cell
    const empty = [];
    for (let r = 0; r < N; r++) {
      for (let c = 0; c < N; c++) {
        if (!s.cells[r][c]){
          empty.push([r, c]);
        }
      }
    }

    //random sort, The Fisher Yates Method
    for(let i = empty.length-1; i > 0; i = i - 1){
      let j = Math.floor(Math.random() * (i+1));
      [empty[i], empty[j]] =[empty[j], empty[i]];
    }

    // put back the random value into random tile
    for(let i = 0; i < values.length; i++){
      let [r,c] = empty[i];
      s.cells[r][c] = values[i];
    }
    
    

  }
  
  // produce negative tiles 
  function makeRandomNegativeTile(s){
    let full_arry = []
  
    let [r, c] = randomPos();
    full_arry.push([r,c]);
    
     // check for empty board cell
    while(s.cells[r][c] !== 0){
      [r, c] = randomPos(); 
      full_arry.push([r,c]);
      console.log('work');
      if(full_arry.length > 16){
          console.log('full')
          return false
      }
    }
    // check if position is valid
    if (r < 0 || r >= N || c < 0 || c >= N) {
        console.log("Invalid position");
        return false;
      }
    s.cells[r][c] = (-1)*(2) ** getRandomInt(1, 3)
  }
  

  // ===== TEST BUTTONS =====

  // Replace random tile
  document.getElementById('btnCreate').addEventListener('click', () => {
    // testing uisng trash point 
    if(State.trashPoint >= 0){
      if(replaceRandomTile(State)){
        //State.trashPoint = State.trashPoint - 1;
        
      }
      render(State);


    }
  });
 
  // Destroy random tile
  document.getElementById('btnDestroy').addEventListener('click', () => {
    const filled = [];

    // collect all non-empty tiles
    for (let r = 0; r < N; r++) {
      for (let c = 0; c < N; c++) {
        if (State.cells[r][c] !== 0) {
          filled.push([r, c]);
        }
      }
    }

    // if no tiles exist, do nothing
    if (filled.length === 0) return;

    // pick random existing tile
    const [r, c] = filled[Math.floor(Math.random() * filled.length)];

    destroySpecificTile(State, r, c);
    render(State);
  });

  // Rearrange board
  document.getElementById('btnShuffle').addEventListener('click', () => {
    rearrangeBoard(State);
    render(State);
  });

  // Make negative tile
  document.getElementById('btnCreateNegative').addEventListener('click', () => {
    makeRandomNegativeTile(State);
    render(State);
  });


})();