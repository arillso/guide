// ============================================
// Arillso Guide - Ultra Modern Interactive JavaScript
// Features: Copy Buttons, Smooth Scroll, Animations
// ============================================

document.addEventListener("DOMContentLoaded", function () {
  // ========================================
  // Text Truncation - Remove descriptions after " – " or " - "
  // Works for breadcrumbs, navigation, and all text elements
  // ========================================
  function truncateDescriptions() {
    // Select all elements that might contain descriptions
    const elements = document.querySelectorAll(
      ".wy-breadcrumbs li a, " +
        ".wy-breadcrumbs li, " +
        ".breadcrumb-item, " +
        ".wy-menu-vertical a, " +
        "h1, h2, h3, h4, h5, h6",
    );

    elements.forEach(function (element) {
      const text = element.textContent;

      // Check for " – " (em dash) or " - " (hyphen dash)
      if (text.includes(" – ")) {
        const parts = text.split(" – ");
        const shortName = parts[0].trim();
        element.setAttribute("title", text);
        element.textContent = shortName;
      } else if (text.includes(" - ")) {
        // Only split on " - " if it looks like a description separator
        // (not just a normal hyphen in a name)
        const parts = text.split(" - ");
        if (parts.length === 2 && parts[1].length > 20) {
          // Likely a description (longer than 20 chars)
          const shortName = parts[0].trim();
          element.setAttribute("title", text);
          element.textContent = shortName;
        }
      }
    });
  }

  // ========================================
  // Code Block Copy Buttons
  // ========================================
  function addCopyButtons() {
    const codeBlocks = document.querySelectorAll(".highlight");

    codeBlocks.forEach(function (block) {
      // Create copy button
      const copyButton = document.createElement("button");
      copyButton.className = "code-copy-button";
      copyButton.textContent = "Copy";
      copyButton.setAttribute("aria-label", "Copy code to clipboard");

      // Add click handler
      copyButton.addEventListener("click", async function () {
        const code = block.querySelector("pre").textContent;

        // Detect code language from CSS classes
        const codeLanguage = detectCodeLanguage(block);

        try {
          await navigator.clipboard.writeText(code);

          // Success feedback
          copyButton.textContent = "Copied!";
          copyButton.classList.add("copied");

          // Track copy event in Umami
          trackEvent("code-copied", {
            language: codeLanguage,
            length: code.length,
          });

          setTimeout(function () {
            copyButton.textContent = "Copy";
            copyButton.classList.remove("copied");
          }, 2000);
        } catch (err) {
          // Fallback for older browsers
          const textArea = document.createElement("textarea");
          textArea.value = code;
          textArea.style.position = "fixed";
          textArea.style.opacity = "0";
          document.body.appendChild(textArea);
          textArea.select();

          try {
            document.execCommand("copy");
            copyButton.textContent = "Copied!";
            copyButton.classList.add("copied");

            // Track copy event in Umami
            trackEvent("code-copied", {
              language: codeLanguage,
              length: code.length,
            });

            setTimeout(function () {
              copyButton.textContent = "Copy";
              copyButton.classList.remove("copied");
            }, 2000);
          } catch (err) {
            copyButton.textContent = "Failed";
            setTimeout(function () {
              copyButton.textContent = "Copy";
            }, 2000);
          }

          document.body.removeChild(textArea);
        }
      });

      // Insert button into code block
      block.style.position = "relative";
      block.appendChild(copyButton);
    });
  }

  // ========================================
  // Detect Code Language from Highlight Classes
  // ========================================
  function detectCodeLanguage(block) {
    const classes = block.className.split(" ");
    for (const className of classes) {
      if (className.startsWith("highlight-")) {
        return className.replace("highlight-", "");
      }
    }
    return "unknown";
  }

  // ========================================
  // Smooth Scroll for Anchor Links
  // ========================================
  function initSmoothScroll() {
    const anchorLinks = document.querySelectorAll('a[href^="#"]');

    anchorLinks.forEach(function (link) {
      link.addEventListener("click", function (e) {
        const targetId = this.getAttribute("href");

        if (targetId === "#") return;

        const targetElement = document.querySelector(targetId);

        if (targetElement) {
          e.preventDefault();
          targetElement.scrollIntoView({
            behavior: "smooth",
            block: "start",
          });

          // Update URL without jumping
          if (history.pushState) {
            history.pushState(null, null, targetId);
          }
        }
      });
    });
  }

  // ========================================
  // Scroll-triggered Animations
  // ========================================
  function initScrollAnimations() {
    const observerOptions = {
      threshold: 0.1,
      rootMargin: "0px 0px -50px 0px",
    };

    const observer = new IntersectionObserver(function (entries) {
      entries.forEach(function (entry) {
        if (entry.isIntersecting) {
          entry.target.style.opacity = "1";
          entry.target.style.transform = "translateY(0)";
        }
      });
    }, observerOptions);

    // Observe feature cards, admonitions, and sections
    const animatedElements = document.querySelectorAll(
      ".feature-card, .admonition, .quickstart-path, .community-card, .stat-card",
    );

    animatedElements.forEach(function (element) {
      element.style.opacity = "0";
      element.style.transform = "translateY(20px)";
      element.style.transition = "opacity 0.6s ease, transform 0.6s ease";
      observer.observe(element);
    });
  }

  // ========================================
  // External Link Icon Enhancement
  // ========================================
  function enhanceExternalLinks() {
    const externalLinks = document.querySelectorAll("a.reference.external");

    externalLinks.forEach(function (link) {
      link.setAttribute("target", "_blank");
      link.setAttribute("rel", "noopener noreferrer");

      // Track external link clicks
      link.addEventListener("click", function () {
        const destination = getExternalLinkDestination(link.href);
        trackEvent("external-link-click", {
          destination: destination,
          url: link.href,
        });
      });
    });
  }

  // ========================================
  // Detect External Link Destination Type
  // ========================================
  function getExternalLinkDestination(url) {
    if (url.includes("github.com")) return "GitHub";
    if (url.includes("hub.docker.com")) return "Docker Hub";
    if (url.includes("galaxy.ansible.com")) return "Ansible Galaxy";
    if (url.includes("github.com/marketplace")) return "GitHub Actions";
    if (url.includes("arillso.io")) return "Arillso Website";
    return "Other";
  }

  // ========================================
  // Table Enhancements - Responsive Scrolling
  // ========================================
  function enhanceTables() {
    const tables = document.querySelectorAll("table");

    tables.forEach(function (table) {
      if (!table.parentElement.classList.contains("wy-table-responsive")) {
        const wrapper = document.createElement("div");
        wrapper.className = "wy-table-responsive";
        table.parentNode.insertBefore(wrapper, table);
        wrapper.appendChild(table);
      }
    });
  }

  // ========================================
  // Keyboard Navigation Enhancement
  // ========================================
  function initKeyboardNav() {
    document.addEventListener("keydown", function (e) {
      // Ctrl/Cmd + K for search focus
      if ((e.ctrlKey || e.metaKey) && e.key === "k") {
        e.preventDefault();
        const searchInput = document.querySelector(
          '.wy-side-nav-search input[type="text"]',
        );
        if (searchInput) {
          searchInput.focus();

          // Track keyboard shortcut usage
          trackEvent("keyboard-shortcut", {
            shortcut: "search-focus",
            key: "Cmd+K",
          });
        }
      }
    });
  }

  // ========================================
  // Back to Top Button
  // ========================================
  function initBackToTop() {
    const backToTopButton = document.createElement("button");
    backToTopButton.className = "back-to-top";
    backToTopButton.innerHTML = "↑";
    backToTopButton.setAttribute("aria-label", "Back to top");
    backToTopButton.style.cssText = `
            position: fixed;
            bottom: 2rem;
            right: 2rem;
            width: 48px;
            height: 48px;
            border-radius: 12px;
            background: linear-gradient(135deg, var(--primary-color) 0%, var(--accent-purple) 100%);
            color: white;
            border: none;
            cursor: pointer;
            opacity: 0;
            pointer-events: none;
            transition: opacity 0.3s, transform 0.3s;
            box-shadow: 0 4px 12px rgba(0, 102, 255, 0.3);
            font-size: 20px;
            font-weight: bold;
            z-index: 1000;
        `;

    document.body.appendChild(backToTopButton);

    // Show/hide based on scroll position
    window.addEventListener("scroll", function () {
      if (window.scrollY > 300) {
        backToTopButton.style.opacity = "1";
        backToTopButton.style.pointerEvents = "auto";
      } else {
        backToTopButton.style.opacity = "0";
        backToTopButton.style.pointerEvents = "none";
      }
    });

    // Scroll to top on click
    backToTopButton.addEventListener("click", function () {
      window.scrollTo({
        top: 0,
        behavior: "smooth",
      });

      // Track back-to-top usage
      trackEvent("navigation", {
        action: "back-to-top",
        scrollPosition: window.scrollY,
      });
    });

    // Hover effect
    backToTopButton.addEventListener("mouseenter", function () {
      this.style.transform = "translateY(-4px)";
    });

    backToTopButton.addEventListener("mouseleave", function () {
      this.style.transform = "translateY(0)";
    });
  }

  // ========================================
  // Performance: Reduce Motion for Users Who Prefer It
  // ========================================
  function respectReducedMotion() {
    const prefersReducedMotion = window.matchMedia(
      "(prefers-reduced-motion: reduce)",
    );

    if (prefersReducedMotion.matches) {
      // Disable animations for users who prefer reduced motion
      const style = document.createElement("style");
      style.textContent = `
                *, *::before, *::after {
                    animation-duration: 0.01ms !important;
                    animation-iteration-count: 1 !important;
                    transition-duration: 0.01ms !important;
                }
            `;
      document.head.appendChild(style);
    }
  }

  // ========================================
  // Mermaid Light Theme Override
  // ========================================
  function initMermaidLightTheme() {
    // Wait for mermaid to be available
    if (typeof mermaid !== "undefined") {
      console.log("Initializing mermaid with light theme");

      mermaid.initialize({
        startOnLoad: true,
        theme: "base",
        themeVariables: {
          primaryColor: "#f0f7ff",
          primaryTextColor: "#1a1a1a",
          primaryBorderColor: "#0066FF",
          lineColor: "#0066FF",
          secondaryColor: "#e6f3ff",
          tertiaryColor: "#ffffff",
          background: "#ffffff",
          mainBkg: "#f0f7ff",
          secondBkg: "#e6f3ff",
          tertiaryBkg: "#ffffff",
          secondaryTextColor: "#1a1a1a",
          tertiaryTextColor: "#1a1a1a",
          textColor: "#1a1a1a",
          nodeTextColor: "#1a1a1a",
          fontSize: "16px",
          nodeBorder: "#0066FF",
          clusterBkg: "#f0f7ff",
          clusterBorder: "#0066FF",
          titleColor: "#1a1a1a",
          edgeLabelBackground: "#ffffff",
          fontFamily:
            '-apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif',
        },
        flowchart: {
          htmlLabels: true,
        },
      });

      // Force re-render all mermaid diagrams
      setTimeout(function () {
        mermaid.run();
      }, 100);
    } else {
      // Retry after a short delay if mermaid isn't loaded yet
      setTimeout(initMermaidLightTheme, 100);
    }
  }

  // ========================================
  // Initialize All Features
  // ========================================
  truncateDescriptions();
  addCopyButtons();
  initSmoothScroll();
  initScrollAnimations();
  enhanceExternalLinks();
  enhanceTables();
  initKeyboardNav();
  initBackToTop();
  respectReducedMotion();
  initMermaidLightTheme();

  console.log(
    "🚀 Arillso Guide: All interactive features loaded successfully!",
  );
});

// ============================================
// Umami Analytics Integration
// Privacy-friendly, GDPR-compliant analytics
// ============================================
(function () {
  const script = document.createElement("script");
  script.defer = true;
  script.src = "https://a.sbaerlo.ch/script.js";
  script.setAttribute("data-website-id", "e0227422-0389-4064-8548-45110a8efd85");

  // Optional: Disable auto-tracking if you want manual control
  // script.setAttribute('data-auto-track', 'false');

  // Optional: Enable domain-specific tracking
  // script.setAttribute('data-domains', 'guide.arillso.io');

  // Optional: Honor Do Not Track browser setting
  script.setAttribute("data-do-not-track", "true");

  document.head.appendChild(script);

  console.log("📊 Umami Analytics: Tracking script loaded");
})();

// ============================================
// Umami Custom Event Tracking Helper
// ============================================
function trackEvent(eventName, eventData) {
  // Wait for umami to be available
  if (typeof umami !== "undefined" && umami.track) {
    umami.track(eventName, eventData);
    console.log("📊 Umami Event:", eventName, eventData);
  } else {
    // Retry after a short delay if umami isn't loaded yet
    setTimeout(function () {
      if (typeof umami !== "undefined" && umami.track) {
        umami.track(eventName, eventData);
        console.log("📊 Umami Event:", eventName, eventData);
      }
    }, 1000);
  }
}

// ============================================
// Track Navigation and Page Sections
// ============================================
document.addEventListener("DOMContentLoaded", function () {
  // Track which documentation section user is viewing
  const currentPath = window.location.pathname;
  let section = "unknown";

  if (currentPath.includes("/guide/getting-started/"))
    section = "Getting Started";
  else if (currentPath.includes("/guide/tutorials/")) section = "Tutorials";
  else if (currentPath.includes("/guide/best-practices/"))
    section = "Best Practices";
  else if (currentPath.includes("/guide/development/")) section = "Development";
  else if (currentPath.includes("/guide/reference/")) section = "Reference";
  else if (currentPath.includes("/containers/")) section = "Containers";
  else if (currentPath.includes("/github/")) section = "GitHub Actions";
  else if (currentPath.includes("/libraries/")) section = "Libraries";
  else if (currentPath === "/" || currentPath === "/index.html")
    section = "Home";

  if (section !== "unknown") {
    trackEvent("page-section-view", {
      section: section,
      path: currentPath,
    });
  }

  // Track sidebar navigation clicks
  const sidebarLinks = document.querySelectorAll(".wy-menu-vertical a");
  sidebarLinks.forEach(function (link) {
    link.addEventListener("click", function () {
      const linkText = this.textContent.trim();
      trackEvent("sidebar-navigation", {
        destination: linkText,
        currentSection: section,
      });
    });
  });

  // Track search usage (when search box is focused and used)
  const searchInput = document.querySelector(
    '.wy-side-nav-search input[type="text"]',
  );
  if (searchInput) {
    let searchStartTime = null;

    searchInput.addEventListener("focus", function () {
      searchStartTime = Date.now();
      trackEvent("search-started", {
        section: section,
      });
    });

    searchInput.addEventListener("blur", function () {
      if (this.value.length > 0 && searchStartTime) {
        const timeSpent = Math.round((Date.now() - searchStartTime) / 1000);
        trackEvent("search-completed", {
          query: this.value,
          timeSpent: timeSpent,
          section: section,
        });
      }
    });
  }

  // Track scroll depth (25%, 50%, 75%, 100%)
  const scrollDepths = [25, 50, 75, 100];
  const triggered = {};

  window.addEventListener("scroll", function () {
    const scrollHeight =
      document.documentElement.scrollHeight - window.innerHeight;
    const scrolled = (window.scrollY / scrollHeight) * 100;

    scrollDepths.forEach(function (depth) {
      if (scrolled >= depth && !triggered[depth]) {
        triggered[depth] = true;
        trackEvent("scroll-depth", {
          depth: depth + "%",
          section: section,
        });
      }
    });
  });

  // Track CTA button clicks
  document.addEventListener("click", function (e) {
    // Hero CTAs
    if (e.target.classList.contains("cta-primary")) {
      trackEvent("cta-click", {
        type: "hero-primary",
        text: e.target.textContent.trim(),
        url: e.target.href,
      });
    }

    if (e.target.classList.contains("cta-secondary")) {
      trackEvent("cta-click", {
        type: "hero-secondary",
        text: e.target.textContent.trim(),
        url: e.target.href,
      });
    }

    // Support CTAs
    if (e.target.closest(".support-btn")) {
      const btn = e.target.closest(".support-btn");
      const strong = btn.querySelector("strong");
      trackEvent("cta-click", {
        type: "support",
        text: strong ? strong.textContent.trim() : "unknown",
        url: btn.href,
      });
    }

    // Help CTAs (troubleshooting page)
    if (e.target.closest(".help-btn")) {
      const btn = e.target.closest(".help-btn");
      const strong = btn.querySelector("strong");
      trackEvent("cta-click", {
        type: "help",
        text: strong ? strong.textContent.trim() : "unknown",
        url: btn.href,
      });
    }

    // Footer CTAs
    if (e.target.closest(".footer-cta .btn-primary-lg")) {
      trackEvent("cta-click", {
        type: "footer-primary",
        text: e.target.textContent.trim(),
        url: e.target.href,
      });
    }

    if (e.target.closest(".footer-cta .btn-secondary-lg")) {
      trackEvent("cta-click", {
        type: "footer-secondary",
        text: e.target.textContent.trim(),
        url: e.target.href,
      });
    }
  });
});
