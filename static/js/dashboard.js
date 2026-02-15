/**
 * Dashboard JavaScript for Smart Office Monitoring System
 * Handles real-time updates and user interactions
 */

// ==================== Auto-Update Functions ====================

/**
 * Update current attendance table
 */
function updateCurrentAttendance() {
    fetch('/api/current_attendance')
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                const tbody = document.querySelector('#currentAttendanceTable tbody');
                if (tbody) {
                    tbody.innerHTML = '';

                    if (data.data.length > 0) {
                        data.data.forEach(record => {
                            const row = `
                                <tr>
                                    <td>${record.employee_name}</td>
                                    <td>${record.department}</td>
                                    <td>${record.entry_time}</td>
                                    <td><span class="badge badge-${record.action}">${record.action}</span></td>
                                </tr>
                            `;
                            tbody.innerHTML += row;
                        });

                        // Update currently inside count
                        const countElement = document.getElementById('currentlyInside');
                        if (countElement) {
                            countElement.textContent = data.data.length;
                        }
                    } else {
                        tbody.innerHTML = '<tr><td colspan="4" class="no-data">No employees currently inside</td></tr>';
                        const countElement = document.getElementById('currentlyInside');
                        if (countElement) {
                            countElement.textContent = '0';
                        }
                    }
                }
            }
        })
        .catch(error => {
            console.error('Error updating attendance:', error);
        });
}

/**
 * Update recent activity table
 */
function updateRecentActivity() {
    fetch('/api/recent_activity')
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                const tbody = document.querySelector('#recentActivityTable tbody');
                if (tbody) {
                    tbody.innerHTML = '';

                    if (data.data.length > 0) {
                        data.data.forEach(record => {
                            const row = `
                                <tr>
                                    <td>${record.employee_name}</td>
                                    <td>${record.department}</td>
                                    <td>${record.entry_time}</td>
                                    <td>${record.exit_time || 'N/A'}</td>
                                    <td><span class="badge badge-${record.status}">${record.status}</span></td>
                                </tr>
                            `;
                            tbody.innerHTML += row;
                        });
                    } else {
                        tbody.innerHTML = '<tr><td colspan="5" class="no-data">No recent activity</td></tr>';
                    }
                }
            }
        })
        .catch(error => {
            console.error('Error updating activity:', error);
        });
}

// ==================== Camera Control Functions ====================

/**
 * Start camera monitoring
 */
function startMonitoring() {
    fetch('/api/start_monitoring', {
        method: 'POST'
    })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                // Update video feed
                const videoFeed = document.getElementById('videoFeed');
                const videoStatus = document.getElementById('videoStatus');

                if (videoFeed) {
                    videoFeed.src = '/video_feed';
                    videoFeed.alt = 'Live camera feed';
                }

                if (videoStatus) {
                    videoStatus.textContent = 'Camera is running. Monitoring active.';
                    videoStatus.style.color = '#2ecc71';
                }

                alert('Monitoring started successfully!');
            } else {
                alert('Error: ' + data.error);
            }
        })
        .catch(error => {
            alert('Error starting monitoring: ' + error.message);
        });
}

/**
 * Stop camera monitoring
 */
function stopMonitoring() {
    fetch('/api/stop_monitoring', {
        method: 'POST'
    })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                // Clear video feed
                const videoFeed = document.getElementById('videoFeed');
                const videoStatus = document.getElementById('videoStatus');

                if (videoFeed) {
                    videoFeed.src = '';
                    videoFeed.alt = 'Camera feed stopped';
                }

                if (videoStatus) {
                    videoStatus.textContent = 'Camera is stopped. Click "Start Monitoring" to begin.';
                    videoStatus.style.color = '#a0a0a0';
                }

                alert('Monitoring stopped.');
            } else {
                alert('Error: ' + data.error);
            }
        })
        .catch(error => {
            alert('Error stopping monitoring: ' + error.message);
        });
}

// ==================== Utility Functions ====================

/**
 * Show notification
 */
function showNotification(message, type = 'info') {
    const notification = document.createElement('div');
    notification.className = `alert alert-${type}`;
    notification.textContent = message;
    notification.style.position = 'fixed';
    notification.style.top = '20px';
    notification.style.right = '20px';
    notification.style.zIndex = '9999';
    notification.style.minWidth = '300px';

    document.body.appendChild(notification);

    setTimeout(() => {
        notification.remove();
    }, 3000);
}

// ==================== Initialize ====================

document.addEventListener('DOMContentLoaded', function () {
    console.log('Smart Office Monitoring System - Dashboard Loaded');

    // Start auto-refresh for attendance if on dashboard
    if (document.getElementById('currentAttendanceTable')) {
        setInterval(updateCurrentAttendance, 3000);
        setInterval(updateRecentActivity, 5000);
    }
});
