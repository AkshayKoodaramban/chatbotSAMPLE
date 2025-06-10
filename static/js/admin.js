import { adminPageData } from './utils.js';

export function initAdminPage() {
    const dropzone = $('#dropzone');
    const fileInput = $('#fileInput');
    const uploadForm = $('#uploadForm');
    const uploadProgress = $('#uploadProgress');
    const progressBar = uploadProgress.find('.progress-bar');
    const documentsList = $('#documentsList');
    const alertContainer = $('#alertContainer');
    const selectAllCheckbox = $('#selectAllCheckbox');
    const deleteSelectedBtn = $('#deleteSelectedBtn');

    function showAlert(type, message) {
        const alert = $(`
            <div class="alert alert-${type} alert-dismissible fade show" role="alert">
                ${message}
                <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
            </div>
        `);
        if (alertContainer.length) {
             alertContainer.append(alert);
        } else {
            $('body').append(alert);
            console.warn("Admin page specific #alertContainer not found, appending to body.");
        }
        setTimeout(() => alert.alert('close'), 5000);
    }
    
    dropzone
        .on('dragover dragenter', function(e) {
            e.preventDefault();
            e.stopPropagation();
            dropzone.addClass('dragover');
        })
        .on('dragleave dragend drop', function(e) {
            e.preventDefault();
            e.stopPropagation();
            dropzone.removeClass('dragover');
        })
        .on('drop', function(e) {
            e.preventDefault();
            e.stopPropagation();
            if (e.originalEvent.dataTransfer && e.originalEvent.dataTransfer.files.length) {
                fileInput[0].files = e.originalEvent.dataTransfer.files;
                updateFileInfo();
            }
        });
    
    $('#browseButton').on('click', function() {
        fileInput.click();
    });
    
    fileInput.on('change', function() {
        updateFileInfo();
    });
    
    uploadForm.on('submit', function(e) {
        e.preventDefault();
        const files = fileInput[0].files;
        if (files.length === 0) {
            showAlert('danger', 'Please select file(s) to upload.');
            return;
        }
        for (let i = 0; i < files.length; i++) {
            if (!files[i].name.toLowerCase().endsWith('.pdf')) {
                showAlert('danger', 'Only PDF files are supported.');
                return;
            }
        }
        uploadFile(files);
    });
    
    function updateFileInfo() {
        const files = fileInput[0].files;
        if (files.length > 0) {
            let html = '';
            for (let i = 0; i < files.length; i++) {
                const file = files[i];
                html += `
                    <div>
                        <i class="fas fa-file-pdf text-danger"></i>
                        <span>${file.name} (${formatFileSize(file.size)})</span>
                    </div>
                `;
            }
            html += `
                <button type="button" class="btn btn-sm btn-outline-danger mt-3" id="removeFileButton">
                    <i class="fas fa-times me-1"></i> Remove
                </button>
            `;
            dropzone.html(html);
            $('#removeFileButton').on('click', function(e) {
                e.preventDefault();
                e.stopPropagation();
                resetFileInput();
            });
        } else {
            resetDropzone();
        }
    }
    
    function resetFileInput() {
        fileInput.val('');
        resetDropzone();
    }
    
    function resetDropzone() {
        dropzone.html(`
            <i class="fas fa-cloud-upload-alt"></i>
            <h4 class="mb-3">Drag and drop PDF files here</h4>
            <p>or</p>
            <button type="button" class="btn btn-primary" id="browseButton">Browse Files</button>
            <small class="d-block mt-2 text-muted">Only PDF files are supported</small>
        `);
        $('#browseButton').on('click', function() {
            fileInput.click();
        });
    }
    
    function formatFileSize(bytes) {
        if (bytes === 0) return '0 Bytes';
        const k = 1024;
        const sizes = ['Bytes', 'KB', 'MB', 'GB', 'TB'];
        const i = Math.floor(Math.log(bytes) / Math.log(k));
        return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
    }
    
    function uploadFile(files) {
        const formData = new FormData();
        for (let i = 0; i < files.length; i++) {
            formData.append('document', files[i]);
        }
        uploadProgress.removeClass('d-none');
        progressBar.css('width', '0%');
        $.ajax({
            url: '/api/upload',
            type: 'POST',
            data: formData,
            processData: false,
            contentType: false,
            xhr: function() {
                const xhr = new window.XMLHttpRequest();
                xhr.upload.addEventListener('progress', function(e) {
                    if (e.lengthComputable) {
                        const percent = Math.round((e.loaded / e.total) * 100);
                        progressBar.css('width', percent + '%');
                    }
                }, false);
                return xhr;
            },
            success: function(response) {
                setTimeout(() => uploadProgress.addClass('d-none'), 500);
                showAlert('success', response.message || 'Document(s) uploaded successfully.');
                resetFileInput();
                loadDocuments();
            },
            error: function(error) {
                uploadProgress.addClass('d-none');
                let errorMessage = 'Error uploading document(s).';
                if (error.responseJSON) {
                    if (error.responseJSON.error) errorMessage = error.responseJSON.error;
                    else if (error.responseJSON.results) errorMessage = error.responseJSON.results.map(r => `${r.filename}: ${r.error || 'Failed'}`).join('<br>');
                }
                showAlert('danger', errorMessage);
            }
        });
    }
    
    function updateDeleteSelectedBtn() {
        const checked = $('.doc-select-checkbox:checked').length;
        deleteSelectedBtn.prop('disabled', checked === 0);
    }

    selectAllCheckbox.on('change', function() {
        $('.doc-select-checkbox').prop('checked', $(this).is(':checked'));
        updateDeleteSelectedBtn();
    });

    deleteSelectedBtn.on('click', function() {
        const selected = $('.doc-select-checkbox:checked').map(function() { return $(this).data('id'); }).get();
        if (selected.length === 0) return;
        if (!confirm(`Are you sure you want to delete ${selected.length} document(s)? This action cannot be undone.`)) return;
        massDeleteDocuments(selected);
    });

    function attachCheckboxEvents() {
        $('.doc-select-checkbox').off('change').on('change', function() {
            const total = $('.doc-select-checkbox').length;
            const checked = $('.doc-select-checkbox:checked').length;
            selectAllCheckbox.prop('checked', total > 0 && checked === total);
            updateDeleteSelectedBtn();
        });
    }

    function massDeleteDocuments(ids) {
        deleteSelectedBtn.prop('disabled', true);
        $.ajax({
            url: '/api/documents/delete',
            type: 'POST',
            contentType: 'application/json',
            data: JSON.stringify({ ids }),
            success: function(response) {
                showAlert('success', response.message || 'Selected documents deleted.');
                (response.deleted_ids || ids).forEach(id => $(`#document-card-${id}`).remove());
                if ($('.doc-select-checkbox').length === 0) {
                    documentsList.html(`<div class="col-12 text-center text-muted"><p>No documents have been uploaded yet.</p></div>`);
                }
                selectAllCheckbox.prop('checked', false);
                updateDeleteSelectedBtn();
            },
            error: function(error) {
                showAlert('danger', (error.responseJSON && error.responseJSON.error) || 'Error deleting selected documents.');
                updateDeleteSelectedBtn();
            }
        });
    }

    function loadDocuments() {
        $.ajax({
            url: '/api/documents',
            type: 'GET',
            success: function(response) {
                const documents = response.documents || [];
                if (documents.length === 0) {
                    documentsList.html(`<div class="col-12 text-center text-muted"><p>No documents have been uploaded yet.</p></div>`);
                    selectAllCheckbox.prop('checked', false);
                    updateDeleteSelectedBtn();
                    return;
                }
                let html = '';
                documents.forEach(function(doc) {
                    const date = new Date(doc.created_at).toLocaleDateString();
                    const displayFilename = doc.display_filename || doc.original_filename || doc.filename;
                    const docId = doc.id || doc.filename;
                    html += `
                        <div class="col-lg-4 col-md-6" id="document-card-${docId}">
                            <div class="card document-card">
                                <div class="card-body d-flex align-items-start">
                                    <input type="checkbox" class="form-check-input doc-select-checkbox select-checkbox mt-1" data-id="${docId}">
                                    <div class="flex-grow-1 ms-2">
                                        <h5 class="card-title mb-1"><i class="fas fa-file-pdf text-danger document-icon"></i> ${displayFilename}</h5>
                                        <p class="card-text text-muted mb-2"><small>Uploaded on ${date}</small></p>
                                        <button class="btn btn-sm btn-outline-danger delete-document-btn" data-id="${docId}"><i class="fas fa-trash-alt me-1"></i> Delete</button>
                                    </div>
                                </div>
                            </div>
                        </div>`;
                });
                documentsList.html(html);
                $('.delete-document-btn').on('click', function() {
                    const documentId = $(this).data('id');
                    if (confirm(`Are you sure you want to delete document: ${documentId}? This action cannot be undone.`)) {
                        deleteDocument(documentId);
                    }
                });
                attachCheckboxEvents();
                selectAllCheckbox.prop('checked', false);
                updateDeleteSelectedBtn();
            },
            error: function(error) {
                showAlert('danger', 'Error loading documents.');
            }
        });
    }
    
    function deleteDocument(documentId) {
        $.ajax({
            url: `/api/document/${documentId}`,
            type: 'DELETE',
            success: function(response) {
                showAlert('success', response.message || 'Document deleted successfully.');
                $(`#document-card-${documentId}`).remove();
                if (documentsList.children().length === 0) {
                    documentsList.html(`<div class="col-12 text-center text-muted"><p>No documents have been uploaded yet.</p></div>`);
                }
                updateDeleteSelectedBtn();
            },
            error: function(error) {
                showAlert('danger', (error.responseJSON && error.responseJSON.error) || 'Error deleting document.');
            }
        });
    }
    
    const adminList = $('#adminList');
    const selectAllAdmins = $('#selectAllAdmins');
    const deleteSelectedAdminsBtn = $('#deleteSelectedAdminsBtn');
    const sidebarSignoutBtn = $('#sidebarSignoutBtn');
    let currentAdmin = adminPageData.adminUsername;

    function loadAdmins() {
        $.get('/api/admins', function(response) {
            const admins = response.admins || [];
            if (admins.length === 0) {
                adminList.html('<div class="text-muted text-center">No admins found.</div>');
                selectAllAdmins.prop('checked', false);
                deleteSelectedAdminsBtn.prop('disabled', true);
                return;
            }
            let html = '';
            admins.forEach(function(username) {
                html += `
                    <div class="admin-list-item" data-username="${username}">
                        <input type="checkbox" class="form-check-input admin-checkbox admin-select-checkbox" data-username="${username}">
                        <span${username === currentAdmin ? ' style="font-weight:bold;"' : ''}>${username}</span>
                        <button class="admin-delete-btn" title="Delete admin" data-username="${username}"><i class="fas fa-trash-alt"></i></button>
                    </div>`;
            });
            adminList.html(html);
            attachAdminSidebarEvents();
        }).fail(function() {
            showAlert('danger', 'Could not load admin users.');
        });
    }

    function attachAdminSidebarEvents() {
        $('.admin-delete-btn').off('click').on('click', function() {
            showSerialKeyModal('single', $(this).data('username'));
        });
        $('.admin-select-checkbox').off('change').on('change', function() {
            updateDeleteSelectedAdminsBtn();
            selectAllAdmins.prop('checked', $('.admin-select-checkbox:checked').length === $('.admin-select-checkbox').length && $('.admin-select-checkbox').length > 0);
        });
    }

    selectAllAdmins.on('change', function() {
        $('.admin-select-checkbox').prop('checked', $(this).is(':checked'));
        updateDeleteSelectedAdminsBtn();
    });

    function updateDeleteSelectedAdminsBtn() {
        deleteSelectedAdminsBtn.prop('disabled', $('.admin-select-checkbox:checked').length === 0);
    }

    deleteSelectedAdminsBtn.on('click', function() {
        const selected = $('.admin-select-checkbox:checked').map(function() { return $(this).data('username'); }).get();
        if (selected.length === 0) return;
        showSerialKeyModal('mass', selected);
    });

    function showSerialKeyModal(actionType, actionTarget) {
        $('#serialKeyInput').val('');
        $('#serialKeyError').text('');
        $('#serialKeyActionType').val(actionType);
        $('#serialKeyActionTarget').val(typeof actionTarget === 'string' ? actionTarget : JSON.stringify(actionTarget));
        const modal = new bootstrap.Modal(document.getElementById('serialKeyModal'));
        modal.show();
    }

    $('#serialKeyForm').on('submit', function(e) {
        e.preventDefault();
        const serialKey = $('#serialKeyInput').val().trim();
        const actionType = $('#serialKeyActionType').val();
        let actionTarget = $('#serialKeyActionTarget').val();
        if (!serialKey) {
            $('#serialKeyError').text('Serial key is required.');
            return;
        }
        $('#serialKeyError').text('');

        const commonError = (xhr, defaultMsg) => {
            let msg = defaultMsg;
            if (xhr.responseJSON && xhr.responseJSON.error) msg = xhr.responseJSON.error;
            $('#serialKeyError').text(msg);
        };

        if (actionType === 'single') {
            $.ajax({
                url: `/api/admin/${actionTarget}`, type: 'DELETE', contentType: 'application/json', data: JSON.stringify({serial_key: serialKey}),
                success: function(response) {
                    $('#serialKeyModal').modal('hide');
                    showAlert('success', response.message || 'Admin deleted.');
                    loadAdmins();
                    if (response.message && response.message.includes('signed out') || (response.self_deleted && actionTarget === currentAdmin)) {
                         setTimeout(() => window.location.href = adminPageData.urls.adminLogin, 1000);
                    }
                },
                error: (xhr) => commonError(xhr, 'Error deleting admin.')
            });
        } else if (actionType === 'mass') {
            let usernames = [];
            try { usernames = JSON.parse(actionTarget); } catch {}
            $.ajax({
                url: '/api/admins/delete', type: 'POST', contentType: 'application/json', data: JSON.stringify({usernames, serial_key: serialKey}),
                success: function(response) {
                    $('#serialKeyModal').modal('hide');
                    if (response.self_deleted) {
                        showAlert('success', 'You deleted your own account and have been signed out.');
                        setTimeout(() => window.location.href = adminPageData.urls.adminLogin, 1000);
                    } else {
                        let successMsg = `Deleted: ${response.deleted.join(', ')}`;
                        if (response.failed && response.failed.length) successMsg += `. Failed: ${response.failed.map(f=>f.username).join(', ')}`;
                        showAlert('success', successMsg);
                    }
                    loadAdmins();
                },
                error: (xhr) => commonError(xhr, 'Error deleting admins.')
            });
        }
    });

    sidebarSignoutBtn.on('click', function() {
        $.get(adminPageData.urls.adminLogout, function() {
            window.location.href = adminPageData.urls.adminLogin;
        });
    });

    let inactivityTimeout;
    function resetInactivityTimer() {
        clearTimeout(inactivityTimeout);
        inactivityTimeout = setTimeout(function() {
            $.get(adminPageData.urls.adminLogout, function() {
                showAlert('info', 'You have been signed out due to inactivity.');
                setTimeout(() => { window.location.href = adminPageData.urls.adminLogin; }, 2000);
            });
        }, 5 * 60 * 1000);
    }
    $(document).on('mousemove keydown click', resetInactivityTimer);
    
    if (adminPageData && adminPageData.isLoggedIn) {
        loadAdmins();
        loadDocuments();
        resetInactivityTimer();
    } else if (!adminPageData.isLoggedIn && document.querySelector('.sidebar-admins')) {
        window.location.href = adminPageData.urls.adminLogin;
    }
}
