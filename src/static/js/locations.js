document.addEventListener('DOMContentLoaded', function() {
  // ===== CONSTANTS =====
  const CONFIG = {
    MAX_LOCATIONS: 5, // Match the parameter from the Jinja2 template
    TIMESTAMP_REFRESH_INTERVAL: 60000 // Update timestamps every minute
  };

  const ENDPOINTS = {
    INITIAL_DATA: '/api/v1/locations/recent', // Endpoint for initial locations data
    SSE_STREAM: '/api/v1/streams/locations'   // Endpoint for SSE updates
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
    locationsList: document.getElementById('locationsList'),
    locationsCount: document.getElementById('locationsCount'),
    widget: document.querySelector('.visitors-locations-widget')
  };

  const CSS_CLASSES = {
    PULSE: 'pulse',
    KEYBOARD_FOCUS: 'keyboard-focus',
    TOUCH_DEVICE: 'touch-device',
    EXPANDED: 'expanded',
    LOCATION_NEW: 'location-new',
    LOCATION_ICON: 'location-icon',
    LOCATION_TEXT: 'location-text',
    LOCATION_TIME: 'location-time',
    LOCATION_PLACEHOLDER: 'location-placeholder'
  };

  const DEFAULT_VALUES = {
    NO_VISITORS: `<li class="${CSS_CLASSES.LOCATION_PLACEHOLDER}">No visitors yet</li>`,
    UNAVAILABLE: `<li class="${CSS_CLASSES.LOCATION_PLACEHOLDER}">Not available</li>`,
    ERROR_TEXT: 'N/A',
    DEFAULT_COUNT: '0'
  };

  const LOCATION_ICON_SVG = '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" width="16" height="16"><path fill="currentColor" d="M12 2C8.13 2 5 5.13 5 9c0 5.25 7 13 7 13s7-7.75 7-13c0-3.87-3.13-7-7-7zm0 9.5c-1.38 0-2.5-1.12-2.5-2.5s1.12-2.5 2.5-2.5 2.5 1.12 2.5 2.5-1.12 2.5-2.5 2.5z"/></svg>';

  // ===== STATE VARIABLES =====
  let locationCache = [];
  let connectionFailed = false;
  let eventSource = null;
  let timestampRefreshInterval = null;

  // ===== INITIALIZATION =====
  function initializeUI() {
    // Initialize with default values to show immediately
    UI_ELEMENTS.locationsCount.textContent = DEFAULT_VALUES.DEFAULT_COUNT;
    UI_ELEMENTS.locationsList.innerHTML = DEFAULT_VALUES.NO_VISITORS;

    // Add keyboard accessibility
    UI_ELEMENTS.widget.setAttribute('tabindex', '0');
    UI_ELEMENTS.widget.addEventListener('keypress', handleKeyboardInteraction);

    // Support for touch devices
    if ('ontouchstart' in window) {
      UI_ELEMENTS.widget.classList.add(CSS_CLASSES.TOUCH_DEVICE);
      UI_ELEMENTS.widget.addEventListener('click', handleTouchInteraction);
    }

    // Setup timestamp refresh interval
    setupTimestampRefresh();
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
    window.addEventListener('beforeunload', cleanupResources);
    window.addEventListener('unload', cleanupResources);

    document.addEventListener('visibilitychange', function() {
      if (document.visibilityState === 'hidden') {
        // When tab becomes hidden, close the connection
        cleanupSSE();
      } else if (document.visibilityState === 'visible' && !eventSource) {
        // When tab becomes visible again and there's no active connection, reconnect
        connectToSSE();
      }
    });

    window.addEventListener('pagehide', cleanupResources);
    window.addEventListener('popstate', function() {
      cleanupSSE();
      setTimeout(connectToSSE, TIMEOUTS.SHORT_DELAY);
    });
  }

  // ===== UTILITY FUNCTIONS =====
  function formatTimeAgo(timestamp) {
    const now = new Date();
    const visitTime = new Date(timestamp);
    const diffSeconds = Math.floor((now - visitTime) / 1000);

    if (diffSeconds < 60) {
      return 'just now';
    } else if (diffSeconds < 3600) {
      const minutes = Math.floor(diffSeconds / 60);
      return `${minutes}m ago`;
    } else if (diffSeconds < 86400) {
      const hours = Math.floor(diffSeconds / 3600);
      return `${hours}h ago`;
    } else {
      const days = Math.floor(diffSeconds / 86400);
      return `${days}d ago`;
    }
  }

  function setupTimestampRefresh() {
    // Clear any existing interval
    if (timestampRefreshInterval) {
      clearInterval(timestampRefreshInterval);
    }

    // Refresh timestamps every minute
    timestampRefreshInterval = setInterval(() => {
      if (!connectionFailed && locationCache.length > 0) {
        // Only update the timestamps, not the whole list
        const timeElements = UI_ELEMENTS.locationsList.querySelectorAll(`.${CSS_CLASSES.LOCATION_TIME}`);
        locationCache.forEach((location, index) => {
          if (timeElements[index]) {
            timeElements[index].textContent = formatTimeAgo(location.timestamp);
          }
        });
      }
    }, CONFIG.TIMESTAMP_REFRESH_INTERVAL);
  }

  function cleanupResources() {
    cleanupSSE();

    // Clear the timestamp refresh interval
    if (timestampRefreshInterval) {
      clearInterval(timestampRefreshInterval);
      timestampRefreshInterval = null;
    }
  }

  // ===== UI UPDATES =====
  function updateLocationsList() {
    // Clear the list
    UI_ELEMENTS.locationsList.innerHTML = '';

    if (locationCache.length === 0) {
      UI_ELEMENTS.locationsList.innerHTML = connectionFailed ?
                                      DEFAULT_VALUES.UNAVAILABLE :
                                      DEFAULT_VALUES.NO_VISITORS;
      return;
    }

    // Add each location to the list
    locationCache.forEach((location, index) => {
      const listItem = document.createElement('li');
      listItem.className = index === 0 ? CSS_CLASSES.LOCATION_NEW : '';

      const iconElement = document.createElement('span');
      iconElement.className = CSS_CLASSES.LOCATION_ICON;
      iconElement.innerHTML = LOCATION_ICON_SVG;

      const textElement = document.createElement('span');
      textElement.className = CSS_CLASSES.LOCATION_TEXT;
      textElement.textContent = location.location;

      const timeElement = document.createElement('span');
      timeElement.className = CSS_CLASSES.LOCATION_TIME;
      timeElement.textContent = formatTimeAgo(location.timestamp);

      listItem.appendChild(iconElement);
      listItem.appendChild(textElement);
      listItem.appendChild(timeElement);

      UI_ELEMENTS.locationsList.appendChild(listItem);
    });
  }

  function updateLocationsCount() {
    UI_ELEMENTS.locationsCount.textContent = locationCache.length;
    UI_ELEMENTS.locationsCount.classList.add(CSS_CLASSES.PULSE);

    setTimeout(() => {
      UI_ELEMENTS.locationsCount.classList.remove(CSS_CLASSES.PULSE);
    }, TIMEOUTS.ANIMATION);
  }

  function showConnectionError() {
    if (connectionFailed) return; // Avoid repeated updates

    connectionFailed = true;
    UI_ELEMENTS.locationsCount.textContent = DEFAULT_VALUES.ERROR_TEXT;
    UI_ELEMENTS.locationsCount.classList.add(CSS_CLASSES.PULSE);

    setTimeout(() => {
      UI_ELEMENTS.locationsCount.classList.remove(CSS_CLASSES.PULSE);
    }, TIMEOUTS.ANIMATION);

    updateLocationsList();
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
              if (data.locations && Array.isArray(data.locations)) {
                resolve(data.locations.slice(0, CONFIG.MAX_LOCATIONS));
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

          if (data.locations && Array.isArray(data.locations)) {
            // Update the locations cache with the latest data
            locationCache = data.locations.slice(0, CONFIG.MAX_LOCATIONS);
            updateLocationsList();
            updateLocationsCount();
          } else if (data.location && data.timestamp) {
            // Single new location update
            // Add to the front of the cache
            locationCache.unshift(data);

            // Limit the cache size
            if (locationCache.length > CONFIG.MAX_LOCATIONS) {
              locationCache.pop();
            }

            updateLocationsList();
            updateLocationsCount();
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
      .then(locations => {
        locationCache = locations;
        updateLocationsList();
        updateLocationsCount();

        if (typeof EventSource !== 'undefined') {
          scheduleSSEConnection();
        } else {
          console.error('Browser does not support Server-Sent Events');
        }
      })
      .catch(error => {
        console.error('Error fetching initial locations data:', error);
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
