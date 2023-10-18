fetch('http://127.0.0.1:8080/').then((response) => {
  response.text().then((text) => console.log(text));
});
