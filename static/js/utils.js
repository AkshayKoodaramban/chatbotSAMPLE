// Utility functions

export function formatMarkdown(text) {
    text = text.replace(/#{6}\s+(.*)/g, '<h6>$1</h6>');
    text = text.replace(/#{5}\s+(.*)/g, '<h5>$1</h5>');
    text = text.replace(/#{4}\s+(.*)/g, '<h4>$1</h4>');
    text = text.replace(/#{3}\s+(.*)/g, '<h3>$1</h3>');
    text = text.replace(/#{2}\s+(.*)/g, '<h2>$1</h2>');
    text = text.replace(/#{1}\s+(.*)/g, '<h1>$1</h1>');
    text = text.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>');
    text = text.replace(/__(.*?)__/g, '<strong>$1</strong>');
    text = text.replace(/\*(.*?)\*/g, '<em>$1</em>');
    text = text.replace(/_(.*?)_/g, '<em>$1</em>');
    text = text.replace(/```([^`]+)```/g, '<pre><code>$1</code></pre>');
    text = text.replace(/`([^`]+)`/g, '<code>$1</code>');
    text = text.replace(/^\s*[-*+]\s+(.*)/gm, '<li>$1</li>');
    text = text.replace(/(<li>.*<\/li>)(?!\s*<li>)/gs, '<ul>$1</ul>');
    text = text.replace(/^\s*\d+\.\s+(.*)/gm, '<li>$1</li>');
    text = text.replace(/(<li>.*<\/li>)(?!\s*<li>)/gs, '<ol>$1</ol>');
    text = text.replace(/\n\n/g, '<br><br>');
    return text;
}

export function handleError(error, message = "An error occurred. Please try again.") {
    console.error("Error:", error);
    const alertContainer = $("#alertContainer");
    if (alertContainer.length) {
        const alertHtml = `
            <div class="alert alert-danger alert-dismissible fade show" role="alert">
                ${message}
                <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
            </div>
        `;
        alertContainer.append(alertHtml);
        setTimeout(function () {
            alertContainer.find(".alert").alert('close');
        }, 5000);
    } else {
        console.warn("No #alertContainer found for error display. Error:", message);
    }
}

export let adminPageData = {
    isLoggedIn: false,
    adminUsername: "",
    urls: {
        adminLogin: "/admin/login",
        adminLogout: "/admin/logout"
    }
};

export function initializeAdminApp() {
    if (window.adminPageInitialData) {
        adminPageData = { ...adminPageData, ...window.adminPageInitialData };
    }

    if (document.querySelector('.sidebar-admins')) {
        if (!adminPageData.isLoggedIn) {
            window.location.href = adminPageData.urls.adminLogin;
        }
    }
}
