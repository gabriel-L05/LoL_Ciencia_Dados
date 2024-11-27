function setActive(element, pageId) {
    var elements = document.querySelectorAll('.animated-underline');
    elements.forEach(function (el) { el.classList.remove('active'); });
    element.classList.add('active');

    var tabs = document.querySelectorAll('.tabs');
    tabs.forEach(function (tab) { tab.classList.remove('show'); });

    var activePage = document.getElementById(pageId);
     activePage.classList.add('show');
}