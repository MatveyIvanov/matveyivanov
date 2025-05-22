document.addEventListener('DOMContentLoaded', function() {
  // ===== CONSTANTS =====
  const ENDPOINTS = {
    INITIAL_DATA: '/api/v1/visitors',
    SSE_STREAM: SSE_HOST + '/api/v1/visitors/stream'
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
    EXPANDED: 'expanded'
  };

  // ===== STATE VARIABLES =====
  let currentCount = 0;
  let connectionFailed = false;
  let eventSource = null;
  let circleCount = null;

  // ===== INITIALIZATION =====
  function initializeUI() {
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
    } else if (document.visibilityState === 'visible' && !eventSource) {
      // When tab becomes visible again and there's no active connection, reconnect
      connectToSSE();
    }
  }

  function handleNavigation() {
    cleanupSSE();
    // Reconnect if needed - possibly delayed to ensure navigation completes
    setTimeout(connectToSSE, TIMEOUTS.NAVIGATION_DELAY);
  }

  // ===== UI UPDATES =====
  function updateVisitorCount(count) {
    if (count === currentCount && !connectionFailed) return;

    connectionFailed = false;
    currentCount = count;
    UI_ELEMENTS.visitorCount.textContent = count;
    circleCount.textContent = count;

    // Add pulse animation
    UI_ELEMENTS.visitorCount.classList.add(CSS_CLASSES.PULSE);
    circleCount.classList.add(CSS_CLASSES.PULSE);

    // Remove the animation class after it completes
    setTimeout(() => {
      UI_ELEMENTS.visitorCount.classList.remove(CSS_CLASSES.PULSE);
      circleCount.classList.remove(CSS_CLASSES.PULSE);
    }, TIMEOUTS.ANIMATION);
  }

  function showConnectionError() {
    if (connectionFailed) return; // Avoid repeated animations

    connectionFailed = true;
    UI_ELEMENTS.visitorCount.textContent = DEFAULT_VALUES.ERROR_TEXT;
    circleCount.textContent = DEFAULT_VALUES.ERROR_TEXT;

    // Add pulse animation
    UI_ELEMENTS.visitorCount.classList.add(CSS_CLASSES.PULSE);
    circleCount.classList.add(CSS_CLASSES.PULSE);

    // Remove the animation class after it completes
    setTimeout(() => {
      UI_ELEMENTS.visitorCount.classList.remove(CSS_CLASSES.PULSE);
      circleCount.classList.remove(CSS_CLASSES.PULSE);
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
      .then(count => {
        updateVisitorCount(count);

        if (typeof EventSource !== 'undefined') {
          scheduleSSEConnection();
        } else {
          console.error('Browser does not support Server-Sent Events');
        }
      })
      .catch(error => {
        console.error('Error fetching initial visitor count:', error);
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
