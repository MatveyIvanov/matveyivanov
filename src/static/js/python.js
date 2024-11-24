const progresses = document.getElementsByClassName("progress");

progresses.array.forEach(progress => {
    progress.innerHTML = "60%";
    progress.style.width = "60vw";
});
