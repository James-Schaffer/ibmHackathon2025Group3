import "https://cdnjs.cloudflare.com/ajax/libs/Chart.js/2.9.4/Chart.jshttps://cdnjs.cloudflare.com/ajax/libs/Chart.js/2.9.4/Chart.js";

var xValues = ["Italy", "France", "Spain", "USA", "Argentina"];
var yValues = [55, 49, 44, 24, 15];
var barColors = ["red", "green","blue","orange","brown"];

new Chart("myChart", {
  type: "bar",
  data: {
    labels: xValues,
    datasets: [{
      backgroundColor: barColors,
      data: yValues
    }]
  },
  options: {}
});