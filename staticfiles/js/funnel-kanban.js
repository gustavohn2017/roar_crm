/**
 * Funnel Kanban JavaScript - Enhanced Interactions
 * Provides smooth animations, real-time updates, and improved UX
 */

document.addEventListener('DOMContentLoaded', function() {
    // Initialize kanban board
    initializeKanbanBoard();
    
    // Set up auto-refresh
    setupAutoRefresh();
    
    // Initialize tooltips and popovers
    initializeTooltips();
    
    // Setup keyboard shortcuts
    setupKeyboardShortcuts();
    
    // Initialize drag and drop (for future enhancement)
    // initializeDragAndDrop();
});

/**
 * Initialize the kanban board with smooth animations
 */
function initializeKanbanBoard() {
    // Animate cards on load
    const leadCards = document.querySelectorAll('.lead-card');
    leadCards.forEach((card, index) => {
        card.style.opacity = '0';
        card.style.transform = 'translateY(20px)';
        
        setTimeout(() => {
            card.style.transition = 'all 0.3s ease';
            card.style.opacity = '1';
            card.style.transform = 'translateY(0)';
        }, index * 50);
    });
    
    // Add hover effects
    leadCards.forEach(card => {
        card.addEventListener('mouseenter', function() {
            this.style.transform = 'translateY(-2px) scale(1.02)';
            this.style.boxShadow = '0 8px 16px rgba(0,0,0,0.3)';
            this.style.zIndex = '10';
        });
        
        card.addEventListener('mouseleave', function() {
            this.style.transform = 'translateY(0) scale(1)';
            this.style.boxShadow = '0 2px 4px rgba(0,0,0,0.15)';
            this.style.zIndex = '1';
        });
    });
    
    // Animate funnel segments
    const funnelSegments = document.querySelectorAll('.funnel-segment');
    funnelSegments.forEach(segment => {
        segment.addEventListener('mouseenter', function() {
            this.style.filter = 'brightness(1.2) saturate(1.1)';
            this.style.transform = 'scale(1.05)';
        });
        
        segment.addEventListener('mouseleave', function() {
            this.style.filter = 'brightness(1) saturate(1)';
            this.style.transform = 'scale(1)';
        });
        
        // Click animation
        segment.addEventListener('click', function() {
            this.style.transform = 'scale(0.95)';
            setTimeout(() => {
                this.style.transform = 'scale(1.05)';
                setTimeout(() => {
                    this.style.transform = 'scale(1)';
                }, 150);
            }, 100);
        });
    });
}

/**
 * Setup auto-refresh with visual indicator
 */
function setupAutoRefresh() {
    let refreshInterval;
    const refreshButton = document.querySelector('[onclick*="reload"]');
    
    if (refreshButton) {
        // Add refresh indicator
        const indicator = document.createElement('div');
        indicator.className = 'refresh-indicator';
        indicator.innerHTML = '<div class="spinner"></div>';
        indicator.style.cssText = `
            position: fixed;
            top: 20px;
            right: 20px;
            background: var(--kanban-card-bg);
            border: 1px solid var(--kanban-border);
            border-radius: 8px;
            padding: 10px;
            display: none;
            z-index: 1000;
        `;
        document.body.appendChild(indicator);
        
        // Auto-refresh every 2 minutes
        refreshInterval = setInterval(() => {
            showRefreshIndicator();
            setTimeout(() => {
                window.location.reload();
            }, 1000);
        }, 120000);
        
        function showRefreshIndicator() {
            indicator.style.display = 'block';
            indicator.innerHTML = '<i class="bi bi-arrow-clockwise" style="animation: spin 1s linear infinite;"></i> Atualizando...';
        }
    }
}

/**
 * Initialize tooltips for better UX
 */
function initializeTooltips() {
    // Value badges tooltips
    const valueBadges = document.querySelectorAll('.lead-value-badge');
    valueBadges.forEach(badge => {
        badge.title = `Valor potencial: ${badge.textContent}`;
        badge.style.cursor = 'help';
    });
      // Column count tooltips
    const columnCounts = document.querySelectorAll('.kanban-column-count');
    columnCounts.forEach(count => {
        const columnTitle = count.closest('.kanban-column-header').querySelector('.kanban-column-title').textContent;
        count.title = `${count.textContent} leads em ${columnTitle}`;
    });
      // Action button tooltips
    const viewButtons = document.querySelectorAll('.lead-action-btn i.bi-eye');
    viewButtons.forEach(icon => {
        const btn = icon.closest('.lead-action-btn');
        if (btn) btn.title = 'Ver detalhes do lead';
    });
    
    const contactButtons = document.querySelectorAll('.lead-action-btn i.bi-telephone');
    contactButtons.forEach(icon => {
        const btn = icon.closest('.lead-action-btn');
        if (btn) btn.title = 'Registrar contato';
    });
}

/**
 * Setup keyboard shortcuts
 */
function setupKeyboardShortcuts() {
    document.addEventListener('keydown', function(e) {
        // F5 or Ctrl+R - Refresh
        if (e.key === 'F5' || (e.ctrlKey && e.key === 'r')) {
            e.preventDefault();
            showLoadingOverlay();
            window.location.reload();
        }
        
        // Escape - Close any open modals or overlays
        if (e.key === 'Escape') {
            hideLoadingOverlay();
        }
        
        // Arrow keys - Navigate between columns
        if (e.key === 'ArrowLeft' || e.key === 'ArrowRight') {
            navigateColumns(e.key === 'ArrowLeft' ? -1 : 1);
        }
    });
}

/**
 * Navigate between kanban columns
 */
function navigateColumns(direction) {
    const columns = document.querySelectorAll('.kanban-column');
    const activeColumn = document.querySelector('.kanban-column.active') || columns[0];
    let currentIndex = Array.from(columns).indexOf(activeColumn);
    
    // Remove active class from all columns
    columns.forEach(col => col.classList.remove('active'));
    
    // Calculate new index
    currentIndex += direction;
    if (currentIndex < 0) currentIndex = columns.length - 1;
    if (currentIndex >= columns.length) currentIndex = 0;
    
    // Add active class and scroll to column
    const targetColumn = columns[currentIndex];
    targetColumn.classList.add('active');
    targetColumn.scrollIntoView({ behavior: 'smooth', inline: 'center' });
}

/**
 * Show loading overlay
 */
function showLoadingOverlay() {
    const overlay = document.createElement('div');
    overlay.id = 'loadingOverlay';
    overlay.innerHTML = `
        <div class="loading-content">
            <div class="loading-spinner"></div>
            <p>Atualizando dados...</p>
        </div>
    `;
    overlay.style.cssText = `
        position: fixed;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        background: rgba(30, 33, 48, 0.9);
        display: flex;
        align-items: center;
        justify-content: center;
        z-index: 9999;
        color: var(--text-color);
    `;
    document.body.appendChild(overlay);
}

/**
 * Hide loading overlay
 */
function hideLoadingOverlay() {
    const overlay = document.getElementById('loadingOverlay');
    if (overlay) {
        overlay.remove();
    }
}

/**
 * Enhanced card interactions
 */
function enhanceCardInteractions() {
    const leadCards = document.querySelectorAll('.lead-card');
    
    leadCards.forEach(card => {
        // Add click to expand functionality
        card.addEventListener('click', function(e) {
            // Don't expand if clicking on action buttons
            if (e.target.closest('.lead-actions')) return;
            
            this.classList.toggle('expanded');
            
            if (this.classList.contains('expanded')) {
                this.style.maxHeight = this.scrollHeight + 'px';
            } else {
                this.style.maxHeight = '';
            }
        });
        
        // Add context menu (right-click) for quick actions
        card.addEventListener('contextmenu', function(e) {
            e.preventDefault();
            showContextMenu(e, this);
        });
    });
}

/**
 * Show context menu for lead cards
 */
function showContextMenu(event, card) {
    // Remove existing context menus
    const existingMenu = document.querySelector('.context-menu');
    if (existingMenu) existingMenu.remove();
    
    const menu = document.createElement('div');
    menu.className = 'context-menu';
    menu.innerHTML = `
        <div class="context-menu-item" onclick="viewLead(this)">
            <i class="bi bi-eye"></i> Ver Detalhes
        </div>
        <div class="context-menu-item" onclick="contactLead(this)">
            <i class="bi bi-telephone"></i> Registrar Contato
        </div>
        <div class="context-menu-item" onclick="editLead(this)">
            <i class="bi bi-pencil"></i> Editar Lead
        </div>
    `;
    
    menu.style.cssText = `
        position: fixed;
        top: ${event.clientY}px;
        left: ${event.clientX}px;
        background: var(--kanban-card-bg);
        border: 1px solid var(--kanban-border);
        border-radius: 6px;
        box-shadow: var(--kanban-shadow-hover);
        z-index: 1000;
        min-width: 150px;
    `;
    
    document.body.appendChild(menu);
    
    // Remove menu when clicking elsewhere
    document.addEventListener('click', function removeMenu() {
        menu.remove();
        document.removeEventListener('click', removeMenu);
    });
}

/**
 * Enhanced notification system for funnel updates
 */
function showUpdateNotification(message, type = 'info') {
    const notification = document.createElement('div');
    notification.className = `update-notification notification-${type}`;
    notification.innerHTML = `
        <div class="notification-content">
            <i class="bi bi-${getNotificationIcon(type)}"></i>
            <span>${message}</span>
        </div>
    `;
    
    notification.style.cssText = `
        position: fixed;
        top: 20px;
        right: 20px;
        background: var(--kanban-card-bg);
        border: 1px solid var(--accent-color);
        border-radius: 8px;
        padding: 12px 16px;
        color: var(--text-color);
        z-index: 1001;
        transform: translateX(100%);
        transition: transform 0.3s ease;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.3);
        max-width: 300px;
    `;
    
    document.body.appendChild(notification);
    
    // Animate in
    setTimeout(() => {
        notification.style.transform = 'translateX(0)';
    }, 100);
    
    // Auto-remove after 3 seconds
    setTimeout(() => {
        notification.style.transform = 'translateX(100%)';
        setTimeout(() => notification.remove(), 300);
    }, 3000);
}

function getNotificationIcon(type) {
    const icons = {
        'info': 'info-circle',
        'success': 'check-circle',
        'warning': 'exclamation-triangle',
        'error': 'x-circle'
    };
    return icons[type] || 'info-circle';
}

/**
 * Monitor for data changes and show notifications
 */
function initializeChangeMonitoring() {
    const initialCounts = {};
    
    // Store initial counts
    document.querySelectorAll('.column-count').forEach((countEl, index) => {
        initialCounts[index] = parseInt(countEl.textContent);
    });
    
    // Check for changes on refresh
    window.addEventListener('beforeunload', () => {
        localStorage.setItem('funnelCounts', JSON.stringify(initialCounts));
    });
    
    // Check stored counts on load
    const storedCounts = localStorage.getItem('funnelCounts');
    if (storedCounts) {
        const previousCounts = JSON.parse(storedCounts);
        let hasChanges = false;
          document.querySelectorAll('.kanban-column-count').forEach((countEl, index) => {
            const currentCount = parseInt(countEl.textContent);
            const previousCount = previousCounts[index] || 0;
            
            if (currentCount !== previousCount) {
                hasChanges = true;
                const columnTitle = countEl.closest('.kanban-column-header').querySelector('.kanban-column-title').textContent;
                const diff = currentCount - previousCount;
                const message = diff > 0 
                    ? `+${diff} leads em ${columnTitle}`
                    : `${diff} leads em ${columnTitle}`;
                
                showUpdateNotification(message, diff > 0 ? 'success' : 'info');
            }
        });
        
        if (hasChanges) {
            // Update stored counts
            localStorage.setItem('funnelCounts', JSON.stringify(initialCounts));
        }
    }
}

/**
 * Enhanced lead card interactions with visual feedback
 */
function enhanceLeadCardFeedback() {
    document.querySelectorAll('.lead-card').forEach(card => {
        // Add click feedback
        card.addEventListener('click', function(e) {
            if (e.target.closest('.lead-actions')) return;
            
            // Visual feedback
            this.style.transform = 'scale(0.98)';
            setTimeout(() => {
                this.style.transform = '';
            }, 150);
        });
        
        // Add double-click to expand functionality
        let clickCount = 0;
        card.addEventListener('click', function(e) {
            if (e.target.closest('.lead-actions')) return;
            
            clickCount++;
            setTimeout(() => {
                if (clickCount === 1) {
                    // Single click - show quick info
                    showLeadQuickInfo(this);                } else if (clickCount === 2) {
                    // Double click - navigate to details
                    const viewBtn = this.querySelector('.lead-action-btn i.bi-eye');
                    if (viewBtn && viewBtn.closest('.lead-action-btn')) {
                        window.location.href = viewBtn.closest('.lead-action-btn').href;
                    }
                }
                clickCount = 0;
            }, 300);
        });
    });
}

function showLeadQuickInfo(leadCard) {
    const leadTitle = leadCard.querySelector('.lead-title').textContent;
    const leadInfo = Array.from(leadCard.querySelectorAll('.lead-info'))
        .map(info => info.textContent.trim())
        .join(' • ');
    
    showUpdateNotification(`${leadTitle}: ${leadInfo}`, 'info');
}

// Initialize all enhancements
document.addEventListener('DOMContentLoaded', function() {
    initializeChangeMonitoring();
    enhanceLeadCardFeedback();
    
    // Add smooth scroll behavior for funnel segments
    document.querySelectorAll('.funnel-segment').forEach((segment, index) => {
        segment.addEventListener('click', function() {
            const targetColumn = document.querySelectorAll('.kanban-column')[index];
            if (targetColumn) {
                targetColumn.scrollIntoView({ 
                    behavior: 'smooth', 
                    inline: 'center',
                    block: 'nearest'
                });
                
                // Highlight target column temporarily
                targetColumn.style.borderColor = 'var(--accent-color)';
                targetColumn.style.boxShadow = '0 0 0 3px rgba(212, 175, 55, 0.3)';
                
                setTimeout(() => {
                    targetColumn.style.borderColor = '';
                    targetColumn.style.boxShadow = '';                }, 2000);
                
                showUpdateNotification(`Navegando para ${targetColumn.querySelector('.kanban-column-title').textContent}`, 'info');
            }
        });
    });
});
