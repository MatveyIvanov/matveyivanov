document.addEventListener('DOMContentLoaded', function() {
  // ===== CONSTANTS =====
  const CONFIG = {
    MAX_LOCATIONS: 5, // Match the parameter from the Jinja2 template
    TIMESTAMP_REFRESH_INTERVAL: 60000 // Update timestamps every minute
  };

  const ENDPOINTS = {
    INITIAL_DATA: '/api/v1/locations', // Endpoint for initial locations data
    SSE_STREAM: '/api/v1/locations/stream'   // Endpoint for SSE updates
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
    LOCATION_PLACEHOLDER: 'location-placeholder',
    HIDDEN: 'hidden' // Added for hiding widget
  };

  const DEFAULT_VALUES = {
    NO_VISITORS: `<li>No visitors yet</li>`,
    UNAVAILABLE: `<li>Not available</li>`,
    ERROR_TEXT: 'N/A',
    DEFAULT_COUNT: '0'
  };

  const LOCATION_ICON_SVG = '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" width="16" height="16"><path fill="currentColor" d="M12 2C8.13 2 5 5.13 5 9c0 5.25 7 13 7 13s7-7.75 7-13c0-3.87-3.13-7-7-7zm0 9.5c-1.38 0-2.5-1.12-2.5-2.5s1.12-2.5 2.5-2.5 2.5 1.12 2.5 2.5-1.12 2.5-2.5 2.5z"/></svg>';

  // ===== STATE VARIABLES =====
  let locationCache = [];
  let previousLocationCache = [];
  let initialLocationCache = null;
  let connectionFailed = false;
  let eventSource = null;
  let timestampRefreshInterval = null;
  let initialDataFetched = false;
  let widgetInitialized = false;
  let maxRetryAttempts = 3;
  let retryCount = 0;

  function decodeHTMLEntities(text) {
    const textArea = document.createElement('textarea');
    textArea.innerHTML = text;
    return textArea.value;
  }

  // ===== WIDGET VISIBILITY CONTROL =====
  function hideWidget() {
    if (UI_ELEMENTS.widget) {
      UI_ELEMENTS.widget.classList.add(CSS_CLASSES.HIDDEN);
    }
  }

  function showWidget() {
    if (UI_ELEMENTS.widget) {
      UI_ELEMENTS.widget.classList.remove(CSS_CLASSES.HIDDEN);
    }
  }

  // ===== INITIALIZATION =====
  function initializeUI() {
    // Early exit if widget doesn't exist
    if (!UI_ELEMENTS.widget || !UI_ELEMENTS.locationsList || !UI_ELEMENTS.locationsCount) {
      console.error('Locations widget elements not found in DOM');
      return false;
    }

    // Initially hide the widget until we confirm we have data
    hideWidget();

    // Initialize with default values
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

    // Add style for hiding widget if not already in CSS
    if (!document.getElementById('locations-widget-styles')) {
      const style = document.createElement('style');
      style.id = 'locations-widget-styles';
      style.textContent = `.${CSS_CLASSES.HIDDEN} { display: none !important; }`;
      document.head.appendChild(style);
    }

    // Setup timestamp refresh interval
    setupTimestampRefresh();

    return true;
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
      } else if (document.visibilityState === 'visible' && !eventSource && initialDataFetched) {
        // When tab becomes visible again and there's no active connection, reconnect
        connectToSSE();
      }
    });

    window.addEventListener('pagehide', cleanupResources);
    window.addEventListener('popstate', function() {
      cleanupSSE();
      if (initialDataFetched) {
        setTimeout(connectToSSE, TIMEOUTS.SHORT_DELAY);
      }
    });
  }

  // ===== UTILITY FUNCTIONS =====
  function formatTimeAgo(timestamp) {
    const now = new Date();
    const visitTime = new Date(parseInt(timestamp) * 1000);
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
      if (locationCache.length > 0) {
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

  // Compare if two location arrays have the same content
  function locationsAreEqual(locations1, locations2) {
    if (locations1.length !== locations2.length) {
      return false;
    }

    // Compare each location by its timestamp and location text
    for (let i = 0; i < locations1.length; i++) {
      if (locations1[i].timestamp !== locations2[i].timestamp ||
          locations1[i].location !== locations2[i].location) {
        return false;
      }
    }

    return true;
  }

  // ===== UI UPDATES =====
  function updateLocationsList(useAnimation = true, forceUpdate = false) {
    // Check if locations have changed before applying pulse animation
    const locationsChanged = !locationsAreEqual(locationCache, previousLocationCache);
    console.log(locationsChanged);

    if (!locationsChanged && !forceUpdate) {
        return;
    }

    // Clear the list
    UI_ELEMENTS.locationsList.innerHTML = '';

    if (locationCache.length === 0) {
      UI_ELEMENTS.locationsList.innerHTML = connectionFailed && !initialLocationCache ?
                                      DEFAULT_VALUES.UNAVAILABLE :
                                      DEFAULT_VALUES.NO_VISITORS;
      return;
    }

    // Only show widget after we have valid data
    if (!widgetInitialized) {
      showWidget();
      widgetInitialized = true;
    }

    // Add each location to the list
    locationCache.forEach((location, index) => {
      const listItem = document.createElement('li');
      listItem.className = useAnimation && index === 0 ? CSS_CLASSES.LOCATION_NEW : '';

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

  function updateLocationsCount(forcePulse = false) {
    // Set the text content to the number of locations
    UI_ELEMENTS.locationsCount.textContent = locationCache.length;

    // Check if locations have changed before applying pulse animation
    const locationsChanged = !locationsAreEqual(locationCache, previousLocationCache);
    console.log(locationsChanged);

    if (locationsChanged || forcePulse) {
      UI_ELEMENTS.locationsCount.classList.add(CSS_CLASSES.PULSE);

      setTimeout(() => {
        UI_ELEMENTS.locationsCount.classList.remove(CSS_CLASSES.PULSE);
      }, TIMEOUTS.ANIMATION);

      // Update the previous cache to match the current one
      previousLocationCache = JSON.parse(JSON.stringify(locationCache));
    }
  }

  function showConnectionError() {
    if (connectionFailed) return; // Avoid repeated updates

    connectionFailed = true;

    // If we have initial locations data, use that instead of showing error
    if (initialLocationCache && initialLocationCache.length > 0) {
      locationCache = initialLocationCache;
      updateLocationsList(false); // Don't animate when falling back
      updateLocationsCount(false); // Don't pulse if falling back to same data
      return;
    }

    // If no initial data and we can't connect, hide widget
    if (!initialDataFetched) {
      hideWidget();
      return;
    }

    UI_ELEMENTS.locationsCount.textContent = DEFAULT_VALUES.ERROR_TEXT;
    UI_ELEMENTS.locationsCount.classList.add(CSS_CLASSES.PULSE);

    setTimeout(() => {
      UI_ELEMENTS.locationsCount.classList.remove(CSS_CLASSES.PULSE);
    }, TIMEOUTS.ANIMATION);

    updateLocationsList(false);
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
                initialDataFetched = true;
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
    // If too many retries, just use the initial locations data
    if (retryCount >= maxRetryAttempts) {
      if (initialLocationCache && initialLocationCache.length > 0) {
        locationCache = initialLocationCache;
        updateLocationsList(false);
        updateLocationsCount(false); // No pulse for fallback
      } else {
        hideWidget();
      }
      return;
    }

    // Clean up any existing connection first
    cleanupSSE();

    try {
      console.log('Establishing SSE connection...');
      eventSource = new EventSource(ENDPOINTS.SSE_STREAM);
      retryCount++;

      // Set timeout to detect initial connection failure
      const connectionTimeout = setTimeout(() => {
        if (!eventSource || eventSource.readyState !== 1) { // 1 = OPEN
          if (initialLocationCache && initialLocationCache.length > 0) {
            locationCache = initialLocationCache;
            updateLocationsList(false);
            updateLocationsCount(false); // No pulse for fallback
          } else {
            showConnectionError();
          }
          cleanupSSE();
        }
      }, TIMEOUTS.SSE_CONNECTION);

      eventSource.onopen = function() {
        console.log('SSE connection opened');
        clearTimeout(connectionTimeout);
        connectionFailed = false;
        retryCount = 0; // Reset retry counter on successful connection
      };

      eventSource.onmessage = function(event) {
        try {
          const data = JSON.parse(event.data);

          // Store the current locations for comparison
          const oldLocations = JSON.parse(JSON.stringify(locationCache));

          if (data.locations && Array.isArray(data.locations)) {
            // Update the locations cache with the latest data
            locationCache = data.locations.slice(0, CONFIG.MAX_LOCATIONS);
            updateLocationsList();
            updateLocationsCount(); // Will check for changes
          } else if (data.location && data.timestamp) {
            // Single new location update
            // Add to the front of the cache
            locationCache.unshift(data);

            // Limit the cache size
            if (locationCache.length > CONFIG.MAX_LOCATIONS) {
              locationCache.pop();
            }

            updateLocationsList();
            updateLocationsCount(); // Will check for changes
          } else {
            throw new Error('Invalid data format');
          }
        } catch (error) {
          console.error('Error parsing SSE data:', error);

          // Use initial data if SSE fails
          if (initialLocationCache && initialLocationCache.length > 0) {
            locationCache = initialLocationCache;
            updateLocationsList(false);
            updateLocationsCount(false); // No pulse for fallback
          } else {
            showConnectionError();
          }
        }
      };

      eventSource.onerror = function(error) {
        console.error('SSE connection error:', error);
        clearTimeout(connectionTimeout);
        cleanupSSE();

        // Use initial data if SSE fails
        if (initialLocationCache && initialLocationCache.length > 0) {
          locationCache = initialLocationCache;
          updateLocationsList(false);
          updateLocationsCount(false); // No pulse for fallback

          // Only try reconnecting if we've shown something to the user
          setTimeout(connectToSSE, TIMEOUTS.SSE_RECONNECT);
        } else {
          showConnectionError();

          // Try reconnecting with backoff
          if (retryCount < maxRetryAttempts) {
            setTimeout(connectToSSE, TIMEOUTS.SSE_RECONNECT * retryCount);
          } else {
            hideWidget();
          }
        }
      };
    } catch (error) {
      console.error('Failed to create EventSource:', error);

      // Use initial data if SSE fails
      if (initialLocationCache && initialLocationCache.length > 0) {
        locationCache = initialLocationCache;
        updateLocationsList(false);
        updateLocationsCount(false); // No pulse for fallback
      } else {
        showConnectionError();
      }

      cleanupSSE();

      // Retry with backoff
      if (retryCount < maxRetryAttempts) {
        setTimeout(connectToSSE, TIMEOUTS.SSE_RECONNECT * retryCount);
      }
    }
  }

  // ===== INITIALIZATION FLOW =====
  function initializeWidget() {
    setupEventHandlers();

    fetchInitialData()
      .then(locations => {
        locationCache = locations;
        previousLocationCache = JSON.parse(JSON.stringify(locations)); // Initialize previous cache
        initialLocationCache = [...locations]; // Create a copy to fall back to

        updateLocationsList(false, true); // Don't animate initial list
        updateLocationsCount(true); // Force pulse on initial load

        if (typeof EventSource !== 'undefined') {
          scheduleSSEConnection();
        } else {
          console.error('Browser does not support Server-Sent Events');
          // Still show widget with initial data even if SSE not supported
          showWidget();
        }
      })
      .catch(error => {
        console.error('Error fetching initial locations data:', error);

        if (typeof EventSource !== 'undefined') {
          setTimeout(connectToSSE, TIMEOUTS.SHORT_DELAY);
        } else {
          // Hide widget if we can't get initial data and browser doesn't support SSE
          hideWidget();
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
  if (!initializeUI()) {
    console.error('Failed to initialize locations widget UI');
    return; // Exit early if UI initialization fails
  }

  if (document.readyState === 'complete') {
    setTimeout(initializeWidget, 0);
  } else {
    window.addEventListener('load', function() {
      setTimeout(initializeWidget, 0);
    });
  }
});
