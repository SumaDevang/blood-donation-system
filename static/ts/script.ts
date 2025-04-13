interface DonorFormData {
  name: string;
  dob: string;
  bloodType: string;
  contact: string;
  email: string;
  lastDonation: string;
}

function validateForm(): boolean {
  const form = document.getElementById("donorForm") as HTMLFormElement;
  const nameInput = document.getElementById("name") as HTMLInputElement;
  const dobInput = document.getElementById("dob") as HTMLInputElement;
  const contactInput = document.getElementById("contact") as HTMLInputElement;
  const emailInput = document.getElementById("email") as HTMLInputElement;

  if (!nameInput.value.trim()) {
    alert("Name is required.");
    return false;
  }

  if (!dobInput.value) {
    alert("Date of Birth is required.");
    return false;
  }

  const contactRegex = /^\d{3}-\d{3}-\d{4}$/;
  if (!contactRegex.test(contactInput.value)) {
    alert("Contact must be in the format XXX-XXX-XXXX.");
    return false;
  }

  const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
  if (!emailRegex.test(emailInput.value)) {
    alert("Please enter a valid email address.");
    return false;
  }

  return true;
}

document.addEventListener("DOMContentLoaded", () => {
  const form = document.getElementById("donorForm") as HTMLFormElement;
  if (form) {
    form.addEventListener("submit", (event: Event) => {
      if (!validateForm()) {
        event.preventDefault();
      }
    });
  }
});