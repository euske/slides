(async () => { 
  let response = await fetch('http://localhost:8080/');
  let text = await response.text();
  console.log(text); 
})();