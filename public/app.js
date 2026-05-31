const form = document.querySelector("#survey-form");
const statusMessage = document.querySelector("#form-status");

async function readJsonResponse(response) {
  const contentType = response.headers.get("content-type") || "";

  if (contentType.includes("application/json")) {
    try {
      return await response.json();
    } catch (error) {
      throw new Error("The server returned invalid JSON.");
    }
  }

  await response.text();
  throw new Error("Unable to save your response. The server returned an unexpected response.");
}

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

    const result = await readJsonResponse(response);

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
