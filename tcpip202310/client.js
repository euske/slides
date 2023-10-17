let response = await fetch('http://127.0.0.1:8080/');
let text = await response.text();
console.log(text);