var percentageToColor = {
    30: "red",
    70: "orange",
    100: "#0cce6b"
}

window.onload = function() {
    var progresses = document.querySelectorAll(".progress");
    progresses.forEach((progress) => {
        var percentage = parseInt(progress.innerHTML.replace("%", ""));
        for (let [key, value] of Object.entries(percentageToColor)) {
            if (percentage > key) {
                continue;
            }
            progress.style.background = value;
            break;
        }
        progress.style.width = progress.innerHTML;
    });
}