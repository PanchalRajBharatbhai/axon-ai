// Forgot Password JavaScript
const API_URL = '/api';

let userFound = false;
let userEmail = '';

const forgotPasswordForm = document.getElementById('forgotPasswordForm');
const emailInput = document.getElementById('email');
const newPasswordGroup = document.getElementById('newPasswordGroup');
const confirmPasswordGroup = document.getElementById('confirmPasswordGroup');
const newPasswordInput = document.getElementById('newPassword');
const confirmPasswordInput = document.getElementById('confirmPassword');
const strengthBar = document.querySelector('.strength-bar');
const errorDiv = document.getElementById('errorMessage');
const successDiv = document.getElementById('successMessage');

// Password strength indicator
newPasswordInput.addEventListener('input', () => {
    const password = newPasswordInput.value;
    let strength = 0;

    if (password.length >= 6) strength++;
    if (password.length >= 10) strength++;
    if (/[a-z]/.test(password) && /[A-Z]/.test(password)) strength++;
    if (/\d/.test(password)) strength++;
    if (/[^a-zA-Z\d]/.test(password)) strength++;

    if (strength <= 2) {
        strengthBar.className = 'strength-bar weak';
    } else if (strength <= 4) {
        strengthBar.className = 'strength-bar medium';
    } else {
        strengthBar.className = 'strength-bar strong';
    }
});

forgotPasswordForm.addEventListener('submit', async (e) => {
    e.preventDefault();

    errorDiv.style.display = 'none';
    successDiv.style.display = 'none';

    const submitBtn = e.target.querySelector('button[type="submit"]');
    submitBtn.classList.add('loading');

    if (!userFound) {
        // Step 1: Verify email
        const email = emailInput.value;

        try {
            const response = await fetch(`${API_URL}/forgot-password`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ email })
            });

            const data = await response.json();

            if (data.success) {
                userFound = true;
                userEmail = email;

                // Show password fields
                newPasswordGroup.style.display = 'block';
                confirmPasswordGroup.style.display = 'block';
                emailInput.disabled = true;

                successDiv.textContent = 'Email verified! Please enter your new password.';
                successDiv.style.display = 'block';

                document.querySelector('.btn-text').textContent = 'Update Password';
            } else {
                errorDiv.textContent = data.message || 'Email not found';
                errorDiv.style.display = 'block';
            }
        } catch (error) {
            errorDiv.textContent = 'Connection error. Please try again.';
            errorDiv.style.display = 'block';
        }
    } else {
        // Step 2: Update password
        const newPassword = newPasswordInput.value;
        const confirmPassword = confirmPasswordInput.value;

        if (newPassword !== confirmPassword) {
            errorDiv.textContent = 'Passwords do not match';
            errorDiv.style.display = 'block';
            submitBtn.classList.remove('loading');
            return;
        }

        try {
            const response = await fetch(`${API_URL}/reset-password`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    email: userEmail,
                    new_password: newPassword
                })
            });

            const data = await response.json();

            if (data.success) {
                successDiv.textContent = 'Password updated successfully! Redirecting to login...';
                successDiv.style.display = 'block';

                setTimeout(() => {
                    window.location.href = 'index.html';
                }, 2000);
            } else {
                errorDiv.textContent = data.message || 'Password reset failed';
                errorDiv.style.display = 'block';
            }
        } catch (error) {
            errorDiv.textContent = 'Connection error. Please try again.';
            errorDiv.style.display = 'block';
        }
    }

    submitBtn.classList.remove('loading');
});
