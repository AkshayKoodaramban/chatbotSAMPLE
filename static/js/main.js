/**
 * Enterprise Q&A Chatbot - Main JavaScript File (Module Entry Point)
 */

import { initializeAdminApp, adminPageData } from './utils.js';
import { initChatPage } from './chat.js';
import { initAdminPage } from './admin.js';

if (document.querySelector('.sidebar-admins')) {
    initializeAdminApp();
}

$(document).ready(function () {
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });

    if ($('#chatMessages').length && $('#userInput').length && $('#sessionsList').length) {
        initChatPage();
    }

    if ($('#uploadForm').length && $('#documentsList').length && $('.sidebar-admins').length) {
        if (adminPageData.isLoggedIn) {
             initAdminPage();
        } else {
            console.log("Admin page elements found, but user not logged in. Redirect should occur.");
        }
    }
});
