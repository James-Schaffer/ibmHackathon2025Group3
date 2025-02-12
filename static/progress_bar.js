$(document).ready(function() {
    
    var bar = $("#savings_bar");
    var savings = 300;
    var budget = 10000;
    //var savings = {{savings}}

    let progress = ((savings)/(budget*0.0005)).toPrecision(2);
    if (progress >= 0) {
        if (progress <= 100) {
            bar.attr("style", "width: " + progress + "%");
            $("#savings_indicator").attr("style", "width: " + progress + "%");
            $("#savings_indicator").text(progress + "%");
        } else {
            progress = 100;
            bar.attr("style", "width: " + progress + "%");
            $("#savings_indicator").attr("style", "width: " + progress + "%");
            $("#savings_indicator").text(progress + "%");
        };
    } else {
        progress = 0;
        bar.attr("style", "width: " + progress + "%");
        $("#savings_indicator").attr("style", "width: " + progress + "%");
        $("#savings_indicator").text(progress + "%"); 
    };
});