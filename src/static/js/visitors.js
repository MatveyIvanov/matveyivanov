document.addEventListener('DOMContentLoaded', function() {
  // ===== CONSTANTS =====
  const ENDPOINTS = {
    INITIAL_DATA: '/api/v1/visitors',
    SSE_STREAM: '/api/v1/visitors/stream'
  };

  const TIMEOUTS = {
    INITIAL_FETCH: 5000,    // 5 seconds for initial data fetch
    SSE_CONNECTION: 5000,   // 5 seconds to establish SSE connection
    ANIMATION: 500,         // 500ms for UI animations
    SSE_RECONNECT: 10000,   // 10 seconds before SSE reconnect attempts
    IDLE_CALLBACK: 2000,    // 2 seconds max wait for requestIdleCallback
    SHORT_DELAY: 100,       // 100ms delay for setTimeout fallback
    NAVIGATION_DELAY: 500   // 500ms delay before reconnect after navigation
  };

  const UI_ELEMENTS = {
    visitorCount: document.getElementById('visitorCount'),
    widget: document.querySelector('.visitors-widget')
  };

  const DEFAULT_VALUES = {
    INITIAL_COUNT: '0',
    ERROR_TEXT: 'N/A'
  };

  const CSS_CLASSES = {
    CIRCLE_COUNT: 'visitors-circle-count',
    PULSE: 'pulse',
    KEYBOARD_FOCUS: 'keyboard-focus',
    TOUCH_DEVICE: 'touch-device',
    EXPANDED: 'expanded',
    HIDDEN: 'hidden' // Added for hiding widget
  };

  // ===== STATE VARIABLES =====
  let currentCount = 0;
  let connectionFailed = false;
  let eventSource = null;
  let circleCount = null;
  let initialDataFetched = false;
  let initialCountValue = null;
  let maxRetryAttempts = 3;
  let retryCount = 0;
  let widgetInitialized = false;

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
    if (!UI_ELEMENTS.widget || !UI_ELEMENTS.visitorCount) {
      console.error('Visitor widget elements not found in DOM');
      return false;
    }

    // Initially hide the widget until we confirm we have data
    hideWidget();

    // Create circular count element
    circleCount = document.createElement('div');
    circleCount.className = CSS_CLASSES.CIRCLE_COUNT;
    circleCount.textContent = DEFAULT_VALUES.INITIAL_COUNT;
    UI_ELEMENTS.widget.appendChild(circleCount);

    // Initialize with default values to show immediately
    UI_ELEMENTS.visitorCount.textContent = DEFAULT_VALUES.INITIAL_COUNT;

    // Add keyboard accessibility
    UI_ELEMENTS.widget.setAttribute('tabindex', '0');
    UI_ELEMENTS.widget.addEventListener('keypress', handleKeyboardInteraction);

    // Support for touch devices
    if ('ontouchstart' in window) {
      UI_ELEMENTS.widget.classList.add(CSS_CLASSES.TOUCH_DEVICE);
      UI_ELEMENTS.widget.addEventListener('click', handleTouchInteraction);
    }

    // Add style for hiding widget if not already in CSS
    if (!document.getElementById('visitors-widget-styles')) {
      const style = document.createElement('style');
      style.id = 'visitors-widget-styles';
      style.textContent = `.${CSS_CLASSES.HIDDEN} { display: none !important; }`;
      document.head.appendChild(style);
    }

    return true;
  }

  // ===== EVENT HANDLERS =====
  function handleKeyboardInteraction(e) {
    if (e.key === 'Enter' || e.key === ' ') {
      // Toggle a class to mimic hover state for keyboard users
      this.classList.toggle(CSS_CLASSES.KEYBOARD_FOCUS);
    }
  }

  function handleTouchInteraction() {
    this.classList.toggle(CSS_CLASSES.EXPANDED);
  }

  function setupEventHandlers() {
    window.addEventListener('beforeunload', cleanupSSE);
    window.addEventListener('unload', cleanupSSE);
    document.addEventListener('visibilitychange', handleVisibilityChange);
    window.addEventListener('pagehide', cleanupSSE);
    window.addEventListener('popstate', handleNavigation);
  }

  function handleVisibilityChange() {
    if (document.visibilityState === 'hidden') {
      // When tab becomes hidden, close the connection
      cleanupSSE();
    } else if (document.visibilityState === 'visible' && !eventSource && initialDataFetched) {
      // When tab becomes visible again and there's no active connection, reconnect
      connectToSSE();
    }
  }

  function handleNavigation() {
    cleanupSSE();
    // Reconnect if needed - possibly delayed to ensure navigation completes
    if (initialDataFetched) {
      setTimeout(connectToSSE, TIMEOUTS.NAVIGATION_DELAY);
    }
  }

  // ===== UI UPDATES =====
  function updateVisitorCount(count) {
    if (count === currentCount && !connectionFailed) return;

    connectionFailed = false;
    currentCount = count;

    // Only show widget after we have a valid count
    if (!widgetInitialized) {
      showWidget();
      widgetInitialized = true;
    }

    UI_ELEMENTS.visitorCount.textContent = count;
    if (circleCount) circleCount.textContent = count;

    // Add pulse animation
    UI_ELEMENTS.visitorCount.classList.add(CSS_CLASSES.PULSE);
    if (circleCount) circleCount.classList.add(CSS_CLASSES.PULSE);

    // Remove the animation class after it completes
    setTimeout(() => {
      UI_ELEMENTS.visitorCount.classList.remove(CSS_CLASSES.PULSE);
      if (circleCount) circleCount.classList.remove(CSS_CLASSES.PULSE);
    }, TIMEOUTS.ANIMATION);
  }

  function showConnectionError() {
    if (connectionFailed) return; // Avoid repeated animations

    connectionFailed = true;

    // If we have an initial count value, use it instead of showing error
    if (initialCountValue !== null) {
      updateVisitorCount(initialCountValue);
      return;
    }

    // If no initial value and we can't connect, hide widget
    if (!initialDataFetched) {
      hideWidget();
      return;
    }

    // Otherwise show error message
    UI_ELEMENTS.visitorCount.textContent = DEFAULT_VALUES.ERROR_TEXT;
    if (circleCount) circleCount.textContent = DEFAULT_VALUES.ERROR_TEXT;

    // Add pulse animation
    UI_ELEMENTS.visitorCount.classList.add(CSS_CLASSES.PULSE);
    if (circleCount) circleCount.classList.add(CSS_CLASSES.PULSE);

    // Remove the animation class after it completes
    setTimeout(() => {
      UI_ELEMENTS.visitorCount.classList.remove(CSS_CLASSES.PULSE);
      if (circleCount) circleCount.classList.remove(CSS_CLASSES.PULSE);
    }, TIMEOUTS.ANIMATION);
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
              if (data.count !== undefined) {
                initialDataFetched = true;
                initialCountValue = data.count;
                resolve(data.count);
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

      xhr.open('GET', ENDPOINTS.INITIAL_DATA, true);
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
    // If too many retries, just use the initial count
    if (retryCount >= maxRetryAttempts) {
      if (initialCountValue !== null) {
        updateVisitorCount(initialCountValue);
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
          if (initialCountValue !== null) {
            updateVisitorCount(initialCountValue);
          } else {
            showConnectionError();
          }
          cleanupSSE();
        }
      }, TIMEOUTS.SSE_CONNECTION);

      eventSource.onopen = function() {
        console.log('SSE connection opened');
        clearTimeout(connectionTimeout);
        retryCount = 0; // Reset retry counter on successful connection
      };

      eventSource.onmessage = function(event) {
        try {
          const data = JSON.parse(event.data);
          if (data.count !== undefined) {
            updateVisitorCount(data.count);
          } else {
            throw new Error('Invalid data format');
          }
        } catch (error) {
          console.error('Error parsing SSE data:', error);

          // Use initial value if SSE fails
          if (initialCountValue !== null) {
            updateVisitorCount(initialCountValue);
          } else {
            showConnectionError();
          }
        }
      };

      eventSource.onerror = function(error) {
        console.error('SSE connection error:', error);
        clearTimeout(connectionTimeout);
        cleanupSSE();

        // Use initial value if SSE fails
        if (initialCountValue !== null) {
          updateVisitorCount(initialCountValue);

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

      // Use initial value if SSE fails
      if (initialCountValue !== null) {
        updateVisitorCount(initialCountValue);
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
      .then(count => {
        initialCountValue = count;
        updateVisitorCount(count);

        if (typeof EventSource !== 'undefined') {
          scheduleSSEConnection();
        } else {
          console.error('Browser does not support Server-Sent Events');
          // Still show widget with initial count even if SSE not supported
          showWidget();
        }
      })
      .catch(error => {
        console.error('Error fetching initial visitor count:', error);

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
    console.error('Failed to initialize visitor widget UI');
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
