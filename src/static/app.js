document.addEventListener("DOMContentLoaded", () => {
  const activitiesList = document.getElementById("activities-list");
  const activitySelect = document.getElementById("activity");
  const signupForm = document.getElementById("signup-form");
  const messageDiv = document.getElementById("message");

  // Function to fetch activities from API
  async function fetchActivities() {
    try {
      const response = await fetch("/activities");
      const activities = await response.json();

      // Clear loading message
      activitiesList.innerHTML = "";

      // Populate activities list
      Object.entries(activities).forEach(([name, details]) => {
        const activityCard = document.createElement("div");
        activityCard.className = "activity-card";

        const spotsLeft = details.max_participants - details.participants.length;

        // Build participants HTML: avatar + name/email or a fallback message
        let participantsHTML = "";
        if (Array.isArray(details.participants) && details.participants.length > 0) {
          participantsHTML = '<ul class="participants-list">';
          participantsHTML += details.participants
            .map((p) => {
              // compute initials from local part of email or string parts
              const local = (p || "").split("@")[0] || p || "";
              const parts = local.split(/[\.\-_+]/).filter(Boolean);
              const initials = parts.length
                ? parts.map((s) => s[0].toUpperCase()).slice(0, 2).join("")
                : (local.slice(0, 2) || p).toUpperCase();
              return `<li data-email="${p}" data-activity="${name}">
                        <span class="avatar" title="${p}">${initials}</span>
                        <span class="participant-name">${p}</span>
                        <button class="delete-btn" title="Remove participant">✕</button>
                      </li>`;
            })
            .join("");
          participantsHTML += "</ul>";
        } else {
          participantsHTML = '<p class="no-participants">No participants yet</p>';
        }

        activityCard.innerHTML = `
          <h4>${name}</h4>
          <p>${details.description}</p>
          <p><strong>Schedule:</strong> ${details.schedule}</p>
          <p><strong>Availability:</strong> ${spotsLeft} spots left</p>
          <div class="participants-section">
            <h5>Participants</h5>
            ${participantsHTML}
          </div>
        `;

        activitiesList.appendChild(activityCard);

        // Add delete button listeners
        const deleteButtons = activityCard.querySelectorAll(".delete-btn");
        deleteButtons.forEach((btn) => {
          btn.addEventListener("click", handleDeleteParticipant);
        });

        // Add option to select dropdown
        const option = document.createElement("option");
        option.value = name;
        option.textContent = name;
        activitySelect.appendChild(option);
      });
    } catch (error) {
      activitiesList.innerHTML = "<p>Failed to load activities. Please try again later.</p>";
      console.error("Error fetching activities:", error);
    }
  }

  // Handle participant deletion
  async function handleDeleteParticipant(event) {
    event.preventDefault();
    const btn = event.target;
    const li = btn.closest("li");
    const email = li.getAttribute("data-email");
    const activity = li.getAttribute("data-activity");

    try {
      const response = await fetch(
        `/activities/${encodeURIComponent(activity)}/unregister?email=${encodeURIComponent(email)}`,
        {
          method: "POST",
        }
      );

      if (response.ok) {
        // Remove the participant from the DOM
        li.remove();
        messageDiv.textContent = `Removed ${email} from ${activity}`;
        messageDiv.className = "success";
        messageDiv.classList.remove("hidden");
        setTimeout(() => {
          messageDiv.classList.add("hidden");
        }, 5000);
      } else {
        const result = await response.json();
        messageDiv.textContent = result.detail || "Failed to remove participant";
        messageDiv.className = "error";
        messageDiv.classList.remove("hidden");
      }
    } catch (error) {
      messageDiv.textContent = "Failed to remove participant. Please try again.";
      messageDiv.className = "error";
      messageDiv.classList.remove("hidden");
      console.error("Error removing participant:", error);
    }
  }

  // Handle form submission
  signupForm.addEventListener("submit", async (event) => {
    event.preventDefault();

    const email = document.getElementById("email").value;
    const activity = document.getElementById("activity").value;

    try {
      const response = await fetch(
        `/activities/${encodeURIComponent(activity)}/signup?email=${encodeURIComponent(email)}`,
        {
          method: "POST",
        }
      );

      const result = await response.json();

      if (response.ok) {
        messageDiv.textContent = result.message;
        messageDiv.className = "success";
        signupForm.reset();
        // Refresh activities to show updated participant list and spots
        fetchActivities();
      } else {
        messageDiv.textContent = result.detail || "An error occurred";
        messageDiv.className = "error";
      }

      messageDiv.classList.remove("hidden");

      // Hide message after 5 seconds
      setTimeout(() => {
        messageDiv.classList.add("hidden");
      }, 5000);
    } catch (error) {
      messageDiv.textContent = "Failed to sign up. Please try again.";
      messageDiv.className = "error";
      messageDiv.classList.remove("hidden");
      console.error("Error signing up:", error);
    }
  });

  // Initialize app
  fetchActivities();
});
