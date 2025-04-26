// Save Gemini key
document.getElementById('keyForm').addEventListener('submit', function(e) {
    e.preventDefault();
    const key = document.getElementById('geminiKey').value.trim();
    chrome.storage.local.set({ geminiKey: key }, function() {
      alert('Gemini API Key saved!');
      document.getElementById('geminiKey').value = '';
    });
  });
  
  // On math form submit, retrieve Gemini key and send with problem
  document.getElementById('mathForm').addEventListener('submit', async (e) => {
    e.preventDefault();
    const problem = document.getElementById('problem').value.trim();
    const resultDiv = document.getElementById('result');
    resultDiv.textContent = "Solving...";
  
    chrome.storage.local.get('geminiKey', async function(data) {
      const geminiKey = data.geminiKey || '';
      try {
        const response = await fetch('http://localhost:5000/solve', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ problem, gemini_key: geminiKey })
        });
        const resData = await response.json();
        resultDiv.textContent = resData.result;
      } catch (err) {
        resultDiv.textContent = "⚠️ Error: Could not connect to backend.";
      }
    });
  });