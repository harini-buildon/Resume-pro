/**
 * static/js/main.js – Frontend Logic
 * ==================================
 * Handles interactive elements, drag-and-drop file uploads,
 * client-side file validation, and UI animations.
 */

document.addEventListener('DOMContentLoaded', function() {
    
    // ──────────────────────────────────────────────────────────
    // 1. Navigation Active Link Helper
    // ──────────────────────────────────────────────────────────
    const currentPath = window.location.pathname;
    const navLinks = document.querySelectorAll('#main-navbar .nav-link');
    
    navLinks.forEach(link => {
        const href = link.getAttribute('href');
        if (href && (currentPath === href || (href !== '/' && currentPath.startsWith(href)))) {
            link.parentElement.classList.add('active');
        }
    });

    // ──────────────────────────────────────────────────────────
    // 2. Drag & Drop Resume Upload Handling
    // ──────────────────────────────────────────────────────────
    const dropZone = document.getElementById('drop-zone');
    const fileInput = document.getElementById('resume-file');
    const uploadForm = document.getElementById('upload-form');
    
    if (dropZone && fileInput) {
        const dropZoneContent = dropZone.querySelector('.drop-zone-content');
        const fileSelected = document.getElementById('file-selected');
        const fileNameEl = document.getElementById('file-name');
        const fileSizeEl = document.getElementById('file-size');
        const removeFileBtn = document.getElementById('remove-file');
        const uploadBtn = document.getElementById('upload-btn');
        const btnText = document.getElementById('btn-text');
        const btnSpinner = document.getElementById('btn-spinner');

        // Helper to format file sizes
        function formatBytes(bytes, decimals = 2) {
            if (bytes === 0) return '0 Bytes';
            const k = 1024;
            const dm = decimals < 0 ? 0 : decimals;
            const sizes = ['Bytes', 'KB', 'MB', 'GB'];
            const i = Math.floor(Math.log(bytes) / Math.log(k));
            return parseFloat((bytes / Math.pow(k, i)).toFixed(dm)) + ' ' + sizes[i];
        }

        // Show selected file state in the UI
        function showFileState(file) {
            if (!file) return;
            
            // Client side validation of extension
            const ext = file.name.split('.').pop().toLowerCase();
            if (ext !== 'pdf' && ext !== 'docx') {
                alert("Only PDF and DOCX files are allowed!");
                resetUploadForm();
                return;
            }

            // Client side validation of size (16MB)
            if (file.size > 16 * 1024 * 1024) {
                alert("File size exceeds 16MB limit!");
                resetUploadForm();
                return;
            }

            fileNameEl.textContent = file.name;
            fileSizeEl.textContent = `(${formatBytes(file.size)})`;
            
            dropZoneContent.classList.add('d-none');
            fileSelected.classList.remove('d-none');
            dropZone.classList.add('border-primary');
            
            // Enable upload button
            uploadBtn.removeAttribute('disabled');
        }

        // Reset the form back to initial drag/drop state
        function resetUploadForm() {
            fileInput.value = '';
            dropZoneContent.classList.remove('d-none');
            fileSelected.classList.add('d-none');
            dropZone.classList.remove('border-primary');
            uploadBtn.setAttribute('disabled', 'true');
        }

        // Click on drop zone to trigger input click
        dropZone.addEventListener('click', () => {
            // Only trigger if input isn't already open and no file is selected
            if (fileInput.value === '') {
                fileInput.click();
            }
        });

        // Trigger change when file selected via file explorer
        fileInput.addEventListener('change', (e) => {
            if (e.target.files.length > 0) {
                showFileState(e.target.files[0]);
            }
        });

        // Drag & Drop events
        ['dragenter', 'dragover'].forEach(eventName => {
            dropZone.addEventListener(eventName, (e) => {
                e.preventDefault();
                e.stopPropagation();
                dropZone.classList.add('dragover');
            }, false);
        });

        ['dragleave', 'drop'].forEach(eventName => {
            dropZone.addEventListener(eventName, (e) => {
                e.preventDefault();
                e.stopPropagation();
                dropZone.classList.remove('dragover');
            }, false);
        });

        dropZone.addEventListener('drop', (e) => {
            const dt = e.dataTransfer;
            const files = dt.files;
            if (files.length > 0) {
                fileInput.files = files;
                showFileState(files[0]);
            }
        });

        // Remove selected file click handler
        removeFileBtn.addEventListener('click', (e) => {
            e.stopPropagation();
            resetUploadForm();
        });

        // Show spinner on form submission
        uploadForm.addEventListener('submit', () => {
            uploadBtn.setAttribute('disabled', 'true');
            btnText.textContent = "Processing Resume...";
            btnSpinner.classList.remove('d-none');
        });
    }

    // ──────────────────────────────────────────────────────────
    // 3. ATS Score Circle Ring Animation
    // ──────────────────────────────────────────────────────────
    const scoreCircle = document.querySelector('.ats-score-circle');
    if (scoreCircle) {
        const scoreRing = scoreCircle.querySelector('.score-ring');
        const scoreNumberEl = document.getElementById('ats-score-number');
        const finalScore = parseInt(scoreCircle.getAttribute('data-score')) || 0;
        
        // Stroke dasharray properties
        const circumference = 326.73; // 2 * pi * r (2 * 3.14159 * 52)
        
        // Start from empty ring (strokeDashoffset = circumference)
        scoreRing.style.strokeDashoffset = circumference;
        
        // Determine ring color based on score
        if (finalScore >= 70) {
            scoreRing.style.stroke = '#059669'; // Success green
        } else if (finalScore >= 50) {
            scoreRing.style.stroke = '#d97706'; // Warning amber
        } else {
            scoreRing.style.stroke = '#dc2626'; // Danger red
        }
        
        // Animate count-up number
        let currentCount = 0;
        const duration = 1000; // 1s
        const startTime = performance.now();
        
        function animateScore(timestamp) {
            const elapsed = timestamp - startTime;
            const progress = Math.min(elapsed / duration, 1);
            
            // Easing function (easeOutQuad)
            const easeProgress = progress * (2 - progress);
            
            // Update number
            currentCount = Math.round(easeProgress * finalScore);
            scoreNumberEl.textContent = currentCount;
            
            // Update stroke offset
            const offset = circumference - (easeProgress * finalScore / 100) * circumference;
            scoreRing.style.strokeDashoffset = offset;
            
            if (progress < 1) {
                requestAnimationFrame(animateScore);
            } else {
                scoreNumberEl.textContent = finalScore;
            }
        }
        
        // Delay animation slightly for page transition
        setTimeout(() => {
            requestAnimationFrame(animateScore);
        }, 150);
    }

    // ──────────────────────────────────────────────────────────
    // 4. Real-time 3D Card Tilt Effect on Mouse Move
    // ──────────────────────────────────────────────────────────
    const tiltCards = document.querySelectorAll('.glass-card, .feature-card, .upload-card, .job-rec-card, .card');
    
    tiltCards.forEach(card => {
        card.style.transformStyle = 'preserve-3d';
        card.style.transition = 'transform 0.15s ease-out, box-shadow 0.3s ease';

        card.addEventListener('mousemove', (e) => {
            const rect = card.getBoundingClientRect();
            const x = e.clientX - rect.left; // cursor position within card
            const y = e.clientY - rect.top;
            
            const centerX = rect.width / 2;
            const centerY = rect.height / 2;
            
            // Calculate tilt angle (-8deg to +8deg)
            const rotateX = ((y - centerY) / centerY) * -7;
            const rotateY = ((x - centerX) / centerX) * 7;
            
            card.style.transform = `perspective(1000px) rotateX(${rotateX}deg) rotateY(${rotateY}deg) translateZ(10px) scale(1.02)`;
        });

        card.addEventListener('mouseleave', () => {
            card.style.transition = 'transform 0.5s ease-out, box-shadow 0.5s ease';
            card.style.transform = 'perspective(1000px) rotateX(0deg) rotateY(0deg) translateZ(0px) scale(1)';
        });
    });
});
