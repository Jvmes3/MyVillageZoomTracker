const form = document.querySelector("#survey-form");
const statusMessage = document.querySelector("#form-status");

form.addEventListener("submit", async (event) => {
  event.preventDefault();

  const formData = new FormData(form);
  const payload = Object.fromEntries(formData.entries());

  statusMessage.textContent = "Submitting your response...";
  statusMessage.classList.remove("error");

  try {
    const response = await fetch("/api/surveys", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify(payload),
    });

    const result = await response.json();

    if (!response.ok || !result.ok) {
      throw new Error(result.error || "Unable to save your response.");
    }

    form.reset();
    statusMessage.textContent = "Thanks. Your attendance and participation response has been saved.";
  } catch (error) {
    statusMessage.textContent = error.message;
    statusMessage.classList.add("error");
  }
});
