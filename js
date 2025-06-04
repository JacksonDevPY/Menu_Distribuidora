const express = require('express');
const app = express();
const port = process.env.PORT || 4000; // Usa a porta da variável de ambiente ou 4000 como padrão

app.get('/', (req, res) => {
  res.send('Hello World!');
});

app.listen(port, () => {
  console.log(`Example app listening on port ${port}`);
});
