// Copy Server Address Utility
function copyAddress() {
    const address = document.getElementById('server-url').innerText;
    navigator.clipboard.writeText(address).then(() => {
        const copyBtn = document.getElementById('copy-btn');
        copyBtn.innerText = 'Copied! ✅';
        setTimeout(() => {
            copyBtn.innerText = 'Copy Link 📋';
        }, 2000);
    }).catch(err => {
        console.error('Could not copy text: ', err);
    });
}

// Main Interactive Operations
document.addEventListener('DOMContentLoaded', () => {
    // Theme Management
    const toggleThemeBtn = document.getElementById('theme-toggle');
    const htmlEl = document.documentElement;

    const currentTheme = localStorage.getItem('theme') || (window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light');
    htmlEl.setAttribute('data-theme', currentTheme);
    updateThemeToggleIcon(currentTheme);

    if (toggleThemeBtn) {
        toggleThemeBtn.addEventListener('click', () => {
            const current = htmlEl.getAttribute('data-theme');
            const target = current === 'dark' ? 'light' : 'dark';
            htmlEl.setAttribute('data-theme', target);
            localStorage.setItem('theme', target);
            updateThemeToggleIcon(target);
        });
    }

    function updateThemeToggleIcon(theme) {
        if (toggleThemeBtn) {
            toggleThemeBtn.textContent = theme === 'dark' ? '☀️' : '🌙';
        }
    }

    // Sidebar Tab Switching & Session Storage Persistence
    const menuItems = document.querySelectorAll('.menu-item');
    const tabContents = document.querySelectorAll('.tab-content');

    const savedActiveTab = sessionStorage.getItem('activeTab') || 'tab-upload';
    setActiveTab(savedActiveTab);

    menuItems.forEach(item => {
        item.addEventListener('click', () => {
            const targetTabId = item.getAttribute('data-target');
            setActiveTab(targetTabId);
            sessionStorage.setItem('activeTab', targetTabId);
        });
    });

    function setActiveTab(tabId) {
        menuItems.forEach(btn => {
            if (btn.getAttribute('data-target') === tabId) {
                btn.classList.add('active');
            } else {
                btn.classList.remove('active');
            }
        });

        tabContents.forEach(content => {
            if (content.id === tabId) {
                content.classList.add('active');
            } else {
                content.classList.remove('active');
            }
        });
    }

    // Drag & Drop Functionality
    const dropZone = document.getElementById('drop-zone');
    const fileInput = document.getElementById('file-input');
    const filePreview = document.getElementById('file-preview');
    const filePreviewList = document.getElementById('file-preview-list');
    const uploadBtn = document.getElementById('upload-btn');

    if (dropZone && fileInput) {
        ['dragenter', 'dragover'].forEach(eventName => {
            dropZone.addEventListener(eventName, (e) => {
                e.preventDefault();
                dropZone.classList.add('drag-over');
            }, false);
        });

        ['dragleave', 'drop'].forEach(eventName => {
            dropZone.addEventListener(eventName, (e) => {
                e.preventDefault();
                dropZone.classList.remove('drag-over');
            }, false);
        });

        dropZone.addEventListener('drop', (e) => {
            const dt = e.dataTransfer;
            const files = dt.files;
            fileInput.files = files;
            updateFilePreview();
        }, false);

        dropZone.addEventListener('click', () => {
            fileInput.click();
        });

        fileInput.addEventListener('change', updateFilePreview);
    }

    function formatBytes(bytes, decimals = 2) {
        if (bytes === 0) return '0 Bytes';
        const k = 1024;
        const dm = decimals < 0 ? 0 : decimals;
        const sizes = ['Bytes', 'KB', 'MB', 'GB', 'TB'];
        const i = Math.floor(Math.log(bytes) / Math.log(k));
        return parseFloat((bytes / Math.pow(k, i)).toFixed(dm)) + ' ' + sizes[i];
    }

    function updateFilePreview() {
        if (!filePreviewList || !filePreview || !uploadBtn) return;
        
        filePreviewList.innerHTML = '';
        const files = fileInput.files;
        
        if (files.length > 0) {
            filePreview.style.display = 'block';
            uploadBtn.removeAttribute('disabled');
            
            const title = document.createElement('div');
            title.style.fontWeight = '600';
            title.style.marginBottom = '0.3rem';
            title.textContent = `Selected (${files.length}) files:`;
            filePreviewList.appendChild(title);
            
            const ul = document.createElement('ul');
            ul.className = 'preview-list-items';
            
            for (let i = 0; i < files.length; i++) {
                const li = document.createElement('li');
                li.innerHTML = `<span style="word-break: break-all; font-weight: 500;">${files[i].name}</span> <span class="muted-text">(${formatBytes(files[i].size)})</span>`;
                ul.appendChild(li);
            }
            filePreviewList.appendChild(ul);
        } else {
            filePreview.style.display = 'none';
            uploadBtn.setAttribute('disabled', 'true');
        }
    }

    // Live Search Filter
    const searchInput = document.getElementById('search-input');
    if (searchInput) {
        searchInput.addEventListener('input', function() {
            const query = this.value.toLowerCase();
            const fileRows = document.querySelectorAll('.file-row');
            fileRows.forEach(row => {
                const filename = row.getAttribute('data-filename').toLowerCase();
                if (filename.includes(query)) {
                    row.style.display = '';
                } else {
                    row.style.display = 'none';
                }
            });
        });
    }
});
