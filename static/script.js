let mining = false;
  // start mining
  const mine = () => {
    console.log("trying to mine")
    mining = true;
    fetch("/mine", {header:'Access-Control-Allow-Origin: *'})
      .then(response => response.json())
      .then(response => {console.log(response); if (mining === true) mine()})
  }
  // stop minig
  const stop = () => { mining = false; }
  // Display the state of the chain
  const chain = () => {
    mining = false;
    fetch("/chain", {header:'Access-Control-Allow-Origin: *'})
      .then(response => response.json())
      .then(response => {console.log(response);})
  }

  // listeners
  document.getElementById("mine").addEventListener("click", () => mine());
  document.getElementById("stop").addEventListener("click", () => stop());
  document.getElementById("chain").addEventListener("click", () => chain());