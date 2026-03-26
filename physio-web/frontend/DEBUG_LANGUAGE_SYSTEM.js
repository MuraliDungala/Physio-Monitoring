/**
 * LANGUAGE SYSTEM DEBUG & FIX SCRIPT
 * Run this in browser console (F12 > Console tab) to test and fix language system
 */

console.clear();
console.log('%c=== LANGUAGE SYSTEM DEBUG SCRIPT ===', 'font-size: 16px; font-weight: bold; color: #1E88E5;');

// ============================================================================
// TEST 1: Check if i18n module loaded
// ============================================================================
console.log('\n%c✓ TEST 1: i18n Module Check', 'color: #1E88E5; font-weight: bold;');
if (typeof i18n === 'object') {
    console.log('✅ i18n module is loaded');
    console.log('   Current language:', i18n.getLanguage());
    console.log('   Translation keys count (EN):', Object.keys(i18n.translations.en || {}).length);
    console.log('   Translation keys count (TE):', Object.keys(i18n.translations.te || {}).length);
} else {
    console.error('❌ i18n module NOT loaded - scripts may not have loaded in correct order');
    console.error('   Solution: Reload the page');
}

// ============================================================================
// TEST 2: Check HTML elements
// ============================================================================
console.log('\n%c✓ TEST 2: DOM Elements Check', 'color: #1E88E5; font-weight: bold;');
const langToggle = document.getElementById('langToggle');
const langCode = document.getElementById('langCode');
const languageMenu = document.getElementById('languageMenu');
const langOptions = Array.from(document.querySelectorAll('.lang-option'));

console.log('langToggle button:', langToggle ? '✅ FOUND' : '❌ NOT FOUND');
console.log('langCode span:', langCode ? '✅ FOUND' : '❌ NOT FOUND');
console.log('languageMenu div:', languageMenu ? '✅ FOUND' : '❌ NOT FOUND');
console.log('lang-option buttons:', langOptions.length > 0 ? `✅ FOUND (${langOptions.length})` : '❌ NOT FOUND');

if (!langToggle) {
    console.error(
        '%cMISSING ELEMENTS: Language selector HTML not properly added to index.html',
        'color: red; font-weight: bold;'
    );
}

// ============================================================================
// TEST 3: Check CSS styles
// ============================================================================
console.log('\n%c✓ TEST 3: CSS Styling Check', 'color: #1E88E5; font-weight: bold;');
if (languageMenu) {
    const computedStyle = window.getComputedStyle(languageMenu);
    console.log('   display property:', computedStyle.display);
    console.log('   visibility property:', computedStyle.visibility);
    console.log('   z-index:', computedStyle.zIndex);
    
    if (computedStyle.display === 'none') {
        console.log('✅ Language menu correctly has display: none');
    } else {
        console.warn('⚠️  Language menu should have display: none by default');
    }
}

// ============================================================================
// TEST 4: Test language switching manually
// ============================================================================
console.log('\n%c✓ TEST 4: Manual Language Switch Test', 'color: #1E88E5; font-weight: bold;');
console.log('Running: i18n.setLanguage("te")');
if (typeof i18n === 'object' && typeof i18n.setLanguage === 'function') {
    i18n.setLanguage('te');
    console.log('✅ Language switched to Telugu');
    console.log('   Current:', i18n.getLanguage());
    console.log('   Test key "dashboard" in TE:', i18n.t('dashboard'));
    
    // Switch back
    i18n.setLanguage('en');
    console.log('✅ Language switched back to English');
    console.log('   Test key "dashboard" in EN:', i18n.t('dashboard'));
} else {
    console.error('❌ Cannot switch language - i18n.setLanguage not available');
}

// ============================================================================
// TEST 5: Test click handlers
// ============================================================================
console.log('\n%c✓ TEST 5: Click Handler Test', 'color: #1E88E5; font-weight: bold;');
if (langToggle) {
    console.log('Simulating click on language toggle button...');
    
    langToggle.click();
    console.log('Click simulated');
    
    setTimeout(() => {
        const isVisible = languageMenu?.classList.contains('show');
        console.log(isVisible ? '✅ Menu appeared after click' : '❌ Menu did not appear');
    }, 100);
} else {
    console.error('Cannot test - langToggle element not found');
}

// ============================================================================
// AUTOMATIC FIX: Re-initialize language system
// ============================================================================
console.log('\n%c✓ AUTOMATIC FIX: Re-initializing Language System', 'color: #10B981; font-weight: bold;');
if (typeof initializeLanguageSystem === 'function') {
    console.log('Calling initializeLanguageSystem()...');
    initializeLanguageSystem();
    console.log('✅ Language system re-initialized');
    console.log('⏳ Check the globe icon in topbar - it should now work');
} else {
    console.warn('⚠️  initializeLanguageSystem function not available globally');
    console.log('Attempting to reinitialize from window object...');
    
    // Try to find it in window
    if (window.initializeLanguageSystem) {
        window.initializeLanguageSystem();
        console.log('✅ Found and called initializeLanguageSystem');
    } else {
        console.error('❌ Cannot find initializeLanguageSystem function');
    }
}

// ============================================================================
// SUMMARY
// ============================================================================
console.log('\n%c=== DEBUG SUMMARY ===', 'font-size: 14px; font-weight: bold; color: #1E88E5;');
console.log('%cTo fix language toggle if still not working:', 'font-weight: bold;');
console.log(`
1. Refresh the page (F5)
2. Open DevTools (F12)
3. Go to Console tab
4. Copy this entire script and paste it
5. Press Enter to run all tests
6. Check the output for any ❌ errors
7. If errors appear, report them

Common Issues:
- ❌ i18n module not loaded → Check i18n.js script tag
- ❌ DOM elements not found → Check index.html language selector HTML
- ❌ Click not working → Check browser console for JavaScript errors
`);

console.log('%cDone! Try clicking the globe icon (EN) in the topbar.', 'color: #10B981; font-weight: bold; font-size: 12px;');
