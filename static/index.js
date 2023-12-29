document.getElementById('next').onclick = function(){
    let lists = document.querySelectorAll('.item');
    document.getElementById('slide').appendChild(lists[0]);
}

document.getElementById('prev').onclick = function(){
    let lists = document.querySelectorAll('.item');
    document.getElementById('slide').prepend(lists[lists.length - 1]);
}
  
document.addEventListener("DOMContentLoaded", function() {
    var homeLink = document.getElementById("homeLink");

    homeLink.addEventListener("click", function(event) {
        event.preventDefault(); // Prevent default link behavior

        // Remove the "active" class from all links
        var links = document.querySelectorAll(".header ul li a");
        links.forEach(function(link) {
            link.classList.remove("active");
        });

        // Add the "active" class to the clicked link
        homeLink.classList.add("active");
    });
});



let contact = document.getElementById('contact');



let active = 'contact';
let zIndex = 2;

aHref.forEach(a => {
    a.addEventListener('click', function(event){
        let tab = a.dataset.tab;
        if(tab !== null && tab !== active){

            let activeOld = document.querySelector('.tab.active');
            if(activeOld) activeOld.classList.remove('active');
            active = tab;

            let tabActive = document.getElementById(active);
            zIndex++;
            tabActive.style.zIndex = zIndex;
            tabActive.style.setProperty('--x', event.clientX + 'px');
            tabActive.style.setProperty('--y', event.clientY + 'px');
            tabActive.classList.add('active');
        }
    })
})
