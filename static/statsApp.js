$(document).ready(function() {
    let statsBar = document.getElementById("expenses-bar");

    var tmp= "";
    var foo= 0;

    var purchases = {food : 10.45, travel : 5.97, party : 5.0, alcahol : 8.99, hobby : 5.3, other : 2.25};

    var total = 0.0

    for (i in purchases) {
        total += purchases[i];
    }

    for (i in purchases) {
        var col = parseInt((parseInt(foo)+1) * (190 / Object.keys(purchases).length) ).toString(16);

        col = `00${col}60`;

        tmp += `<div class="expenses-bar-cell" style='width: ${100*purchases[i]/total}%; height: 100%; background-color: #${col};' onmouseover="$('#expenses-hoverLabel').text('${i} : £${purchases[i]}')"></div>`;
    
        foo += 1;
    }

    statsBar.innerHTML = tmp;
});