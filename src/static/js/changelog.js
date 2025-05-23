document.addEventListener('DOMContentLoaded', function() {
  // ===== CONSTANTS =====
  const CONFIG = {
    MAX_UPDATES: 5, // Match the parameter from the Jinja2 template
    NEW_UPDATE_HOURS: 24 // Hours within which an update is considered "new"
  };
  const ENDPOINTS = {
    INITIAL_DATA: '/api/v1/changelog', // Endpoint for initial changelog data
    SSE_STREAM: '/api/v1/changelog/stream'   // Endpoint for SSE updates
  };

  const TIMEOUTS = {
    INITIAL_FETCH: 5000,    // 5 seconds for initial data fetch
    SSE_CONNECTION: 5000,   // 5 seconds to establish SSE connection
    SSE_RECONNECT: 10000,   // 10 seconds before SSE reconnect attempts
    ANIMATION: 500,         // 500ms for UI animations
    IDLE_CALLBACK: 2000,    // 2 seconds max wait for requestIdleCallback
    SHORT_DELAY: 100        // 100ms delay for setTimeout fallback
  };

  const UI_ELEMENTS = {
    changelogList: document.getElementById('changelogList'),
    changelogCount: document.getElementById('changelogCount'),
    widget: document.querySelector('.changelog-widget')
  };

  const CSS_CLASSES = {
    PULSE: 'pulse',
    KEYBOARD_FOCUS: 'keyboard-focus',
    TOUCH_DEVICE: 'touch-device',
    EXPANDED: 'expanded',
    UPDATE_NEW: 'update-new',
    UPDATE_HEADER: 'update-header',
    UPDATE_ICON: 'update-icon',
    UPDATE_TITLE: 'update-title',
    NEW_BADGE: 'new-badge',
    UPDATE_TAG: 'update-tag',
    UPDATE_DESCRIPTION: 'update-description',
    UPDATE_META: 'update-meta',
    UPDATE_VERSION: 'update-version',
    UPDATE_DATE: 'update-date'
  };

  const DEFAULT_VALUES = {
    NO_UPDATES: '<li>No updates yet</li>',
    UNAVAILABLE: '<li>Not available</li>',
    ERROR_TEXT: 'N/A',
    DEFAULT_COUNT: '0'
  };

  const UPDATE_ICONS = {
    FEATURE: '<path fill="currentColor" d="M19 1H9c-1.1 0-2 .9-2 2v3h2V4h10v16H9v-2H7v3c0 1.1.9 2 2 2h10c1.1 0 2-.9 2-2V3c0-1.1-.9-2-2-2zM7.01 13.47l-2.55-2.55-1.41 1.41L7.01 16.3l6.36-6.36-1.41-1.41-4.95 4.94z"/>',
    FIX: '<path fill="currentColor" d="M19.73 14.23L7.71 2.21a.996.996 0 0 0-1.41 0L3.7 4.8a.996.996 0 0 0 0 1.41l12.02 12.02c.39.39 1.02.39 1.41 0l2.59-2.58a.996.996 0 0 0 .01-1.42zM7 16.5c-1.93 0-3.5-1.57-3.5-3.5 0-.58.16-1.12.41-1.6l2.7 2.7c.46.25 1.01.41 1.59.41.45 0 .85-.1 1.24-.26l-2.7-2.7c.16-.39.26-.79.26-1.24 0-.58-.16-1.13-.41-1.59l2.7-2.7c.48.25 1.02.41 1.6.41 1.93 0 3.5 1.57 3.5 3.5 0 .58-.16 1.12-.41 1.6l-2.7-2.7c-.46-.25-1.01-.41-1.59-.41-.45 0-.85.1-1.24.26l2.7 2.7c-.16.39-.26.79-.26 1.24 0 .58.16 1.13.41 1.59l-2.7 2.7c-.48-.25-1.02-.41-1.6-.41z"/>',
    IMPROVEMENT: '<path fill="currentColor" d="M3 17.25V21h3.75L17.81 9.94l-3.75-3.75L3 17.25zM20.71 7.04c.39-.39.39-1.02 0-1.41l-2.34-2.34a.9959.9959 0 0 0-1.41 0l-1.83 1.83 3.75 3.75 1.83-1.83z"/>',
    SECURITY: '<path fill="currentColor" d="M12 1L3 5v6c0 5.55 3.84 10.74 9 12 5.16-1.26 9-6.45 9-12V5l-9-4zm0 10.99h7c-.53 4.12-3.28 7.79-7 8.94V12H5V6.3l7-3.11v8.8z"/>',
    DEFAULT: '<path fill="currentColor" d="M11.99 2C6.47 2 2 6.48 2 12s4.47 10 9.99 10C17.52 22 22 17.52 22 12S17.52 2 11.99 2zm4.24 16L12 15.45 7.77 18l1.12-4.81-3.73-3.23 4.92-.42L12 5l1.92 4.53 4.92.42-3.73 3.23L16.23 18z"/>'
  };

  // ===== STATE VARIABLES =====
  let updatesCache = [];
  let connectionFailed = false;
  let seenUpdateIds = new Set(); // To track which updates the user has seen
  let eventSource = null; // Store the eventSource reference globally for cleanup

  // ===== INITIALIZATION =====
  function initializeUI() {
    // Initialize with default values to show immediately
    UI_ELEMENTS.changelogCount.textContent = DEFAULT_VALUES.DEFAULT_COUNT;
    UI_ELEMENTS.changelogList.innerHTML = DEFAULT_VALUES.NO_UPDATES;

    // Add keyboard accessibility
    UI_ELEMENTS.widget.setAttribute('tabindex', '0');
    UI_ELEMENTS.widget.addEventListener('keypress', handleKeyboardInteraction);

    // Mark updates as seen when the widget is expanded
    UI_ELEMENTS.widget.addEventListener('mouseenter', markUpdatesAsSeen);
    UI_ELEMENTS.widget.addEventListener('focus', markUpdatesAsSeen);
    UI_ELEMENTS.widget.addEventListener('click', markUpdatesAsSeen);

    // Support for touch devices
    if ('ontouchstart' in window) {
      UI_ELEMENTS.widget.classList.add(CSS_CLASSES.TOUCH_DEVICE);
      UI_ELEMENTS.widget.addEventListener('click', handleTouchInteraction);
    }
  }

  // ===== EVENT HANDLERS =====
  function handleKeyboardInteraction(e) {
    if (e.key === 'Enter' || e.key === ' ') {
      this.classList.toggle(CSS_CLASSES.KEYBOARD_FOCUS);
    }
  }

  function handleTouchInteraction() {
    this.classList.toggle(CSS_CLASSES.EXPANDED);
  }

  function setupEventHandlers() {
    window.addEventListener('beforeunload', cleanupSSE);
    window.addEventListener('unload', cleanupSSE);

    document.addEventListener('visibilitychange', function() {
      if (document.visibilityState === 'hidden') {
        // When tab becomes hidden, close the connection
        cleanupSSE();
      } else if (document.visibilityState === 'visible' && !eventSource) {
        // When tab becomes visible again and there's no active connection, reconnect
        connectToSSE();
      }
    });

    window.addEventListener('pagehide', cleanupSSE);
    window.addEventListener('popstate', function() {
      cleanupSSE();
      setTimeout(connectToSSE, TIMEOUTS.SHORT_DELAY);
    });
  }

  // ===== UTILITY FUNCTIONS =====
  function formatDate(dateString) {
    const date = new Date(parseInt(dateString) * 1000);
    const now = new Date();
    const diffMs = now - date;
    const diffDays = Math.floor(diffMs / (1000 * 60 * 60 * 24));

    if (diffDays === 0) {
      return 'Today';
    } else if (diffDays === 1) {
      return 'Yesterday';
    } else if (diffDays < 7) {
      return `${diffDays} days ago`;
    } else {
      const options = { month: 'short', day: 'numeric' };
      if (date.getFullYear() !== now.getFullYear()) {
        options.year = 'numeric';
      }
      return date.toLocaleDateString(undefined, options);
    }
  }

  function getUpdateTypeIcon(type) {
    const lowerType = type.toLowerCase();
    let iconPath;

    switch (lowerType) {
      case 'feature':
        iconPath = UPDATE_ICONS.FEATURE;
        break;
      case 'fix':
        iconPath = UPDATE_ICONS.FIX;
        break;
      case 'improvement':
        iconPath = UPDATE_ICONS.IMPROVEMENT;
        break;
      case 'security':
        iconPath = UPDATE_ICONS.SECURITY;
        break;
      default:
        iconPath = UPDATE_ICONS.DEFAULT;
    }

    return `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" width="16" height="16">${iconPath}</svg>`;
  }

  function isNewUpdate(timestamp) {
    const now = new Date();
    const updateTime = new Date(parseInt(timestamp) * 1000);
    const diffMs = now - updateTime;
    const diffHours = diffMs / (1000 * 60 * 60);

    return diffHours < CONFIG.NEW_UPDATE_HOURS;
  }

  function markUpdatesAsSeen() {
    updatesCache.forEach(update => {
      seenUpdateIds.add(update.id);
    });
    updateChangesCount();
  }

  function countUnseenUpdates() {
    return updatesCache.filter(update => !seenUpdateIds.has(update.id)).length;
  }

  // ===== UI UPDATES =====
  function updateChangelogList() {
    // Clear the list
    UI_ELEMENTS.changelogList.innerHTML = '';

    if (updatesCache.length === 0) {
      UI_ELEMENTS.changelogList.innerHTML = connectionFailed ?
                                      DEFAULT_VALUES.UNAVAILABLE :
                                      DEFAULT_VALUES.NO_UPDATES;
      return;
    }

    // Add each update to the list
    updatesCache.forEach((update, index) => {
      const listItem = document.createElement('li');
      listItem.className = index === 0 && !seenUpdateIds.has(update.id) ? CSS_CLASSES.UPDATE_NEW : '';

      const headerDiv = document.createElement('div');
      headerDiv.className = CSS_CLASSES.UPDATE_HEADER;

      const iconElement = document.createElement('span');
      iconElement.className = `${CSS_CLASSES.UPDATE_ICON} icon-${update.type.toLowerCase()}`;
      iconElement.innerHTML = getUpdateTypeIcon(update.type);

      const titleElement = document.createElement('span');
      titleElement.className = CSS_CLASSES.UPDATE_TITLE;
      titleElement.textContent = update.title;

      // Add NEW badge if this update is new and not seen
      if (isNewUpdate(update.date) && !seenUpdateIds.has(update.id)) {
        const newBadge = document.createElement('span');
        newBadge.className = CSS_CLASSES.NEW_BADGE;
        newBadge.textContent = 'NEW';
        titleElement.appendChild(newBadge);
      }

      const tagElement = document.createElement('span');
      tagElement.className = `${CSS_CLASSES.UPDATE_TAG} update-tag-${update.type.toLowerCase()}`;
      tagElement.textContent = update.type;

      headerDiv.appendChild(iconElement);
      headerDiv.appendChild(titleElement);
      headerDiv.appendChild(tagElement);

      const descriptionElement = document.createElement('div');
      descriptionElement.className = CSS_CLASSES.UPDATE_DESCRIPTION;
      descriptionElement.textContent = update.description;

      const metaDiv = document.createElement('div');
      metaDiv.className = CSS_CLASSES.UPDATE_META;

      const versionElement = document.createElement('span');
      versionElement.className = CSS_CLASSES.UPDATE_VERSION;
      versionElement.textContent = update.version;

      const dateElement = document.createElement('span');
      dateElement.className = CSS_CLASSES.UPDATE_DATE;
      dateElement.textContent = formatDate(update.date);

      metaDiv.appendChild(versionElement);
      metaDiv.appendChild(dateElement);

      listItem.appendChild(headerDiv);
      listItem.appendChild(descriptionElement);
      listItem.appendChild(metaDiv);

      UI_ELEMENTS.changelogList.appendChild(listItem);
    });
  }

  function updateChangesCount() {
    const unseenCount = countUnseenUpdates();
    UI_ELEMENTS.changelogCount.textContent = unseenCount > 0 ? unseenCount : updatesCache.length;
    UI_ELEMENTS.changelogCount.classList.add(CSS_CLASSES.PULSE);

    setTimeout(() => {
      UI_ELEMENTS.changelogCount.classList.remove(CSS_CLASSES.PULSE);
    }, TIMEOUTS.ANIMATION);
  }

  function showConnectionError() {
    if (connectionFailed) return; // Avoid repeated updates

    connectionFailed = true;
    UI_ELEMENTS.changelogCount.textContent = DEFAULT_VALUES.ERROR_TEXT;
    UI_ELEMENTS.changelogCount.classList.add(CSS_CLASSES.PULSE);

    setTimeout(() => {
      UI_ELEMENTS.changelogCount.classList.remove(CSS_CLASSES.PULSE);
    }, TIMEOUTS.ANIMATION);

    updateChangelogList();
  }

  // ===== DATA FETCHING =====
  function fetchInitialData() {
    return new Promise((resolve, reject) => {
      const xhr = new XMLHttpRequest();

      xhr.onreadystatechange = function() {
        if (xhr.readyState === 4) {
          if (xhr.status === 200) {
            try {
              const data = JSON.parse(xhr.responseText);
              if (data.updates && Array.isArray(data.updates)) {
                resolve(data.updates.slice(0, CONFIG.MAX_UPDATES));
              } else {
                reject(new Error('Invalid data format'));
              }
            } catch (error) {
              reject(error);
            }
          } else {
            reject(new Error(`HTTP error: ${xhr.status}`));
          }
        }
      };

      xhr.timeout = TIMEOUTS.INITIAL_FETCH;
      xhr.ontimeout = () => reject(new Error('Request timeout'));

      xhr.open('GET', ENDPOINTS.INITIAL_DATA, true); // Async = true for non-blocking
      xhr.send();
    });
  }

  function cleanupSSE() {
    if (eventSource) {
      console.log('Closing SSE connection...');
      eventSource.close();
      eventSource = null;
    }
  }

  function connectToSSE() {
    // Clean up any existing connection first
    cleanupSSE();

    try {
      console.log('Establishing SSE connection...');
      eventSource = new EventSource(ENDPOINTS.SSE_STREAM);

      // Set timeout to detect initial connection failure
      const connectionTimeout = setTimeout(() => {
        if (!eventSource || eventSource.readyState !== 1) { // 1 = OPEN
          showConnectionError();
          cleanupSSE();
        }
      }, TIMEOUTS.SSE_CONNECTION);

      eventSource.onopen = function() {
        console.log('SSE connection opened');
        clearTimeout(connectionTimeout);
        connectionFailed = false;
      };

      eventSource.onmessage = function(event) {
        try {
          const data = JSON.parse(event.data);

          if (data.updates && Array.isArray(data.updates)) {
            // Update the changelog cache with the latest data
            updatesCache = data.updates.slice(0, CONFIG.MAX_UPDATES);
            updateChangelogList();
            updateChangesCount();
          } else if (data.id && data.title && data.type && data.description && data.version && data.date) {
            // Single new update
            // Check if we already have this update
            const existingIndex = updatesCache.findIndex(update => update.id === data.id);

            if (existingIndex === -1) {
              // It's a new update, add to the front of the cache
              updatesCache.unshift(data);

              // Limit the cache size
              if (updatesCache.length > CONFIG.MAX_UPDATES) {
                updatesCache.pop();
              }

              updateChangelogList();
              updateChangesCount();
            }
          } else {
            throw new Error('Invalid data format');
          }
        } catch (error) {
          console.error('Error parsing SSE data:', error);
          showConnectionError();
        }
      };

      eventSource.onerror = function(error) {
        console.error('SSE connection error:', error);
        clearTimeout(connectionTimeout);
        cleanupSSE();
        showConnectionError();
        setTimeout(connectToSSE, TIMEOUTS.SSE_RECONNECT);
      };
    } catch (error) {
      console.error('Failed to create EventSource:', error);
      showConnectionError();
      cleanupSSE();
      setTimeout(connectToSSE, TIMEOUTS.SSE_RECONNECT);
    }
  }

  // ===== INITIALIZATION FLOW =====
  function initializeWidget() {
    setupEventHandlers();

    fetchInitialData()
      .then(updates => {
        updatesCache = updates;
        updateChangelogList();
        updateChangesCount();

        if (typeof EventSource !== 'undefined') {
          scheduleSSEConnection();
        } else {
          console.error('Browser does not support Server-Sent Events');
        }
      })
      .catch(error => {
        console.error('Error fetching initial changelog data:', error);
        if (typeof EventSource !== 'undefined') {
          setTimeout(connectToSSE, TIMEOUTS.SHORT_DELAY);
        } else {
          showConnectionError();
        }
      });
  }

  function scheduleSSEConnection() {
    if (window.requestIdleCallback) {
      requestIdleCallback(() => connectToSSE(), { timeout: TIMEOUTS.IDLE_CALLBACK });
    } else {
      setTimeout(connectToSSE, TIMEOUTS.SHORT_DELAY);
    }
  }

  // ===== START INITIALIZATION =====
  initializeUI();

  if (document.readyState === 'complete') {
    setTimeout(initializeWidget, 0);
  } else {
    window.addEventListener('load', function() {
      setTimeout(initializeWidget, 0);
    });
  }
});
