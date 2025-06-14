document.addEventListener('DOMContentLoaded', function() {
  // ===== CONSTANTS =====
  const ENDPOINTS = {
    INITIAL_DATA: '/api/v1/visitors', // Endpoint for initial data
    SSE_STREAM: '/api/v1/visitors/stream' // Endpoint for SSE updates
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
    HIDDEN: 'hidden'
  };

  // ===== STATE VARIABLES =====
  let currentCount = 0;
  let connectionFailed = false;
  let eventSource = null;
  let circleCount = null;
  let initialDataFetched = false;
  let initialCountValue = null;
  const maxRetryAttempts = 3;
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
    if (!UI_ELEMENTS.widget || !UI_ELEMENTS.visitorCount) {
      console.error('Visitor widget elements not found in DOM');
      return false;
    }

    hideWidget();

    circleCount = document.createElement('div');
    circleCount.className = CSS_CLASSES.CIRCLE_COUNT;
    circleCount.textContent = DEFAULT_VALUES.INITIAL_COUNT;
    UI_ELEMENTS.widget.appendChild(circleCount);

    UI_ELEMENTS.visitorCount.textContent = DEFAULT_VALUES.INITIAL_COUNT;

    UI_ELEMENTS.widget.setAttribute('tabindex', '0');
    UI_ELEMENTS.widget.addEventListener('keypress', handleKeyboardInteraction);

    if ('ontouchstart' in window) {
      UI_ELEMENTS.widget.classList.add(CSS_CLASSES.TOUCH_DEVICE);
      UI_ELEMENTS.widget.addEventListener('click', handleTouchInteraction);
    }

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
      cleanupSSE();
    } else if (document.visibilityState === 'visible' && !eventSource && initialDataFetched) {
      connectToSSE();
    }
  }

  function handleNavigation() {
    cleanupSSE();
    if (initialDataFetched) {
      setTimeout(connectToSSE, TIMEOUTS.NAVIGATION_DELAY);
    }
  }

  // ===== UI UPDATES =====
  function updateVisitorCount(count) {
    if (count === currentCount && !connectionFailed) return;

    connectionFailed = false;
    currentCount = count;

    if (!widgetInitialized) {
      showWidget();
      widgetInitialized = true;
    }

    UI_ELEMENTS.visitorCount.textContent = count;
    if (circleCount) circleCount.textContent = count;

    UI_ELEMENTS.visitorCount.classList.add(CSS_CLASSES.PULSE);
    if (circleCount) circleCount.classList.add(CSS_CLASSES.PULSE);

    setTimeout(() => {
      UI_ELEMENTS.visitorCount.classList.remove(CSS_CLASSES.PULSE);
      if (circleCount) circleCount.classList.remove(CSS_CLASSES.PULSE);
    }, TIMEOUTS.ANIMATION);
  }

  function showConnectionError() {
    if (connectionFailed) return;

    connectionFailed = true;

    if (initialCountValue !== null) {
      updateVisitorCount(initialCountValue);
      return;
    }

    if (!initialDataFetched) {
      hideWidget();
      return;
    }

    UI_ELEMENTS.visitorCount.textContent = DEFAULT_VALUES.ERROR_TEXT;
    if (circleCount) circleCount.textContent = DEFAULT_VALUES.ERROR_TEXT;

    UI_ELEMENTS.visitorCount.classList.add(CSS_CLASSES.PULSE);
    if (circleCount) circleCount.classList.add(CSS_CLASSES.PULSE);

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
    if (retryCount >= maxRetryAttempts) {
      if (initialCountValue !== null) {
        updateVisitorCount(initialCountValue);
      } else {
        hideWidget();
      }
      return;
    }

    cleanupSSE();

    try {
      console.log('Establishing SSE connection...');
      eventSource = new EventSource(ENDPOINTS.SSE_STREAM);
      retryCount++;

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
        retryCount = 0;
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

        if (initialCountValue !== null) {
          updateVisitorCount(initialCountValue);

          setTimeout(connectToSSE, TIMEOUTS.SSE_RECONNECT);
        } else {
          showConnectionError();

          if (retryCount < maxRetryAttempts) {
            setTimeout(connectToSSE, TIMEOUTS.SSE_RECONNECT * retryCount);
          } else {
            hideWidget();
          }
        }
      };
    } catch (error) {
      console.error('Failed to create EventSource:', error);

      if (initialCountValue !== null) {
        updateVisitorCount(initialCountValue);
      } else {
        showConnectionError();
      }

      cleanupSSE();

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
          showWidget();
        }
      })
      .catch(error => {
        console.error('Error fetching initial visitor count:', error);

        if (typeof EventSource !== 'undefined') {
          setTimeout(connectToSSE, TIMEOUTS.SHORT_DELAY);
        } else {
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
    return;
  }

  if (document.readyState === 'complete') {
    setTimeout(initializeWidget, 0);
  } else {
    window.addEventListener('load', function() {
      setTimeout(initializeWidget, 0);
    });
  }
});
