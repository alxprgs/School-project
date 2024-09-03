document.addEventListener("DOMContentLoaded", function () {
    const form = document.getElementById("auth-form");
    const toggleButton = document.getElementById("toggle-button");
    const registerFields = document.getElementById("register-fields");
    const formTitle = document.getElementById("form-title");
    const submitButton = document.getElementById("submit-button");
    const emailField = document.getElementById("email");
    const passwordRepetitionField = document.getElementById("password-repetition");

    let isRegistering = false; // Переключатель для режима регистрации

    toggleButton.addEventListener("click", function () {
        isRegistering = !isRegistering;
        if (isRegistering) {
            formTitle.textContent = "Регистрация";
            submitButton.textContent = "Зарегистрироваться";
            toggleButton.textContent = "Уже есть аккаунт? Войти";
            registerFields.style.display = "block";
            emailField.required = true;  // Устанавливаем required для email
            passwordRepetitionField.required = true;  // Устанавливаем required для повторного пароля
        } else {
            formTitle.textContent = "Авторизация";
            submitButton.textContent = "Войти";
            toggleButton.textContent = "Нет аккаунта? Зарегистрироваться";
            registerFields.style.display = "none";
            emailField.required = false;  // Удаляем required с email
            passwordRepetitionField.required = false;  // Удаляем required с повторного пароля
        }
    });

    form.addEventListener("submit", async function (event) {
        event.preventDefault();

        const formData = new FormData(form);

        let url = isRegistering ? "/auth/callback/registration" : "/auth/callback/password";

        try {
            const response = await fetch(url, {
                method: "POST",
                body: formData
            });

            const result = await response.json();

            if (response.ok) {
                alert(isRegistering ? "Регистрация прошла успешно!" : "Авторизация прошла успешно!");
                window.location.href = "/";
            } else {
                alert(result.message || "Произошла ошибка");
            }
        } catch (error) {
            console.error("Ошибка:", error);
            alert("Произошла ошибка");
        }
    });
});
