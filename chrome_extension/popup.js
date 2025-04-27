document.addEventListener('DOMContentLoaded', function() {
  // Load saved API key from storage
  chrome.storage.sync.get(['geminiApiKey'], function(result) {
    if (result.geminiApiKey) {
      document.getElementById('apiKey').value = result.geminiApiKey;
    }
  });

  document.getElementById('solve').addEventListener('click', solveProblem);
});

function solveProblem() {
  const apiKey = document.getElementById('apiKey').value;
  const problem = document.getElementById('problem').value;
  const loader = document.getElementById('loader');
  const resultContainer = document.getElementById('result-container');
  const stepsContainer = document.getElementById('steps');
  const finalAnswerContainer = document.getElementById('final-answer');
  
  // Validate inputs
  if (!apiKey) {
    alert('Please enter your Gemini API key');
    return;
  }
  
  if (!problem) {
    alert('Please enter a math problem to solve');
    return;
  }
  
  // Save API key for future use
  chrome.storage.sync.set({geminiApiKey: apiKey});
  
  // Show loader, hide results
  loader.style.display = 'block';
  resultContainer.style.display = 'none';
  stepsContainer.innerHTML = '';
  finalAnswerContainer.innerHTML = '';
  
  // Make API request to Flask server
  fetch('http://localhost:5000/api/solve', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({
      api_key: apiKey,
      problem: problem
    })
  })
  .then(response => response.json())
  .then(data => {
    // Hide loader
    loader.style.display = 'none';
    
    if (data.success) {
      // Show result container
      resultContainer.style.display = 'block';
      
      // Display conversation steps
      if (data.conversation && data.conversation.length > 0) {
        data.conversation.forEach(msg => {
          const stepDiv = document.createElement('div');
          stepDiv.className = `step ${msg.role}`;
          stepDiv.textContent = `${msg.role === 'assistant' ? 'Assistant: ' : 'User: '}${msg.content}`;
          stepsContainer.appendChild(stepDiv);
        });
      }
      
      // Display final answer
      if (data.final_answer) {
        finalAnswerContainer.textContent = `Final Answer: ${data.final_answer}`;
      }
    } else {
      // Show error
      alert(`Error: ${data.error || 'Unknown error occurred'}`);
    }
  })
  .catch(error => {
    loader.style.display = 'none';
    alert(`Network error: ${error.message}`);
    console.error('Error:', error);
  });
}