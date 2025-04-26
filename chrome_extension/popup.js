document.getElementById('solveBtn').addEventListener('click', async () => {
  const problem = document.getElementById('problem').value;
  const resultDiv = document.getElementById('result');
  resultDiv.textContent = "Solving...";

  try {
    const response = await fetch('http://localhost:5000/solve', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ problem })
    });
    const data = await response.json();
    resultDiv.textContent = data.result;
  } catch (err) {
    resultDiv.textContent = "Error: Could not connect to backend.";
  }
});