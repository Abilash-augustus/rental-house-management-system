//building charts
$(function () {        
    var $buildingRentChart = $("#building-rent-chart");
    $.ajax({url: $buildingRentChart.data("url"),success: function (data) {        
        var ctx = $buildingRentChart[0].getContext("2d");        
        new Chart(ctx, {type: 'pie',data: {labels: data.labels,datasets: [{data: data.data,
              backgroundColor: [
              '#fcba03', '#88fc03', '#A9A9A9', '#1daba8', '#3d5454', '#1e3152',
              '#47410b', '#557310', '#277310', '#107331', '#2792b0', '#d47a6a',
              ],}]},options: {responsive: true,legend: {display: false, },
            scales: {yAxes: [{ticks: { display: false,}}]},
            title: {display: true,text: 'Rent Overview'}}});}});});

$(function () {        
   var $buildingVisitsOverview = $("#buildingVisitsOverview");
   $.ajax({url: $buildingVisitsOverview.data("url"),
   success: function (data) {var ctx = $buildingVisitsOverview[0].getContext("2d");        
   new Chart(ctx, {type: 'pie',data: {labels: data.labels,
    datasets: [{label: 'Rent',data: data.data,backgroundColor: [
                '#1e3152','#47410b', '#557310', '#277310', '#107331', '#2792b0', '#d47a6a',
    ],}]},
    options: {responsive: true,legend: {display: true,},
    scales: {yAxes: [{ticks: {display: false,},gridLines: {display:false}}],
    xAxes: [{ticks: {display: false,},gridLines: {display:false}}]},
    title: {display: true,text: 'Visits Overview'}}});}});});

$(function () {        
   var $reportsOverview = $("#reports-overview");
   $.ajax({url: $reportsOverview.data("url"),success: function (data) {
    var ctx = $reportsOverview[0].getContext("2d");        
    new Chart(ctx, {type: 'pie',data: {labels: data.labels,
    datasets: [{label: 'Reports',data: data.data,backgroundColor: [
                  '#fcba03', '#88fc03', '#A9A9A9', '#1daba8', '#3d5454', '#1e3152',
                  '#47410b', '#557310', '#277310', '#107331', '#2792b0', '#d47a6a',],}]},
    options: {responsive: true,legend: {display: false,},scales: {yAxes: [{
                ticks: {display: false,}}]},title: {display: true,text: 'Reports Overview'}}});}});});

$(function () {        
    var $complaintsOverview = $("#complaints_overview");
    $.ajax({url: $complaintsOverview.data("url"),
    success: function (data) {        
    var ctx = $complaintsOverview[0].getContext("2d");        
    new Chart(ctx, {type: 'pie',data: {labels: data.labels,
        datasets: [{label: 'Complaints',data: data.data,backgroundColor: [
            '#2792b0', '#277310', '#d47a6a',],}]},
        options: {responsive: true,legend: {display: false,},scales: {yAxes: [{
            ticks: {display: false,}}]},title: {display: true,text: 'Complaints Overview'}}});}});});

$(function () {        
    var $evictionsChart = $("#evictionsOverview");
    $.ajax({url: $evictionsChart.data("url"),success: function (data) {        
    var ctx = $evictionsChart[0].getContext("2d");        
    new Chart(ctx, {type: 'pie',data: {labels: data.labels,
        datasets: [{label: 'Evictions', data: data.data,backgroundColor: [
                          '#2792b0', '#d47a6a',],}]},options: {responsive: true,
        legend: {display: false,},scales: {yAxes: [{ticks: {display: false,},gridLines: {
          display:false}}],xAxes: [{ticks: {display: false,},gridLines: {display:false }}]},
        title: {display: true,text: 'Evictions Overview'}}});}});});
       
$(function () { var $moveOutNotices = $("#moveoutChart");
    $.ajax({url: $moveOutNotices.data("url"),success: function (data) {
        var ctx = $moveOutNotices[0].getContext("2d");        
        new Chart(ctx, {type: 'pie',data: {labels: data.labels,
            datasets: [{label: 'Notices',data: data.data,backgroundColor: [
                      '#d47a6a', '#fc4103', '#b53c14',],}]},options: {responsive: true,
            legend: {display: false,},scales: {yAxes: [{ticks: {display: false,},
                gridLines: {display:false}}],xAxes: [{ticks: {display: false,},
                 gridLines: {display:false}}]},title: {display: true,text: 'Move Out Notices'}}});}}); });

$(function () {        
    var $unitsChart = $("#unitsOverview");
    $.ajax({url: $unitsChart.data("url"),success: function (data) {
        var ctx = $unitsChart[0].getContext("2d");        
        new Chart(ctx, {type: 'pie', data: {labels: data.labels, 
            datasets: [{label: 'Rent',data: data.data,backgroundColor: [
                    '#1daba8', '#3d5454', '#1e3152','#47410b', '#557310', '#277310', '#107331', '#2792b0', '#d47a6a',
                    ],}]},options: {responsive: true,legend: {display: true,},
                  scales: {yAxes: [{ticks: {display: false, }, gridLines: {display:false}}],
                    xAxes: [{ticks: {display: false,},gridLines: {display:false}}]},
                  title: {display: true,text: 'Units Overview'}}});}});});

//tnants charts
$(function () {var $tenantWaterChart = $("#tenantWaterUsageChart");
$.ajax({url: $tenantWaterChart.data("url"),success: function (data) {
    var ctx = $tenantWaterChart[0].getContext("2d");
    new Chart(ctx, {type: 'line',data: {labels: data.labels,
        datasets: [{label: 'units',backgroundColor: '#d4f1f9',
          data: data.data}]},
          options: {responsive: true,legend: {display: false,},
          scales: {xAxes: [{ticks: {display: false,}}],yAxes: [{
              ticks: {display: true,beginAtZero: true},
            scaleLabel: {display: true,labelString: 'm³'}}]},
          title: {display: true,text: "Water Consumption"}}});}});});

$(function () {var $tenantsElectricityChart = $("#tenantsElectricityUsage");
     $.ajax({url: $tenantsElectricityChart.data("url"),success: function (data) {
        var ctx = $tenantsElectricityChart[0].getContext("2d");
        new Chart(ctx, {type: 'line',data: {labels: data.labels,
        datasets: [{label: 'units',backgroundColor: '#00FFFF',
        data: data.data}]},
        options: {responsive: true,legend: {display: false,},
        scales: {xAxes: [{ticks: {display: false,}}],yAxes: [{
            ticks: {display: true,beginAtZero: true},
        scaleLabel: {display: true,labelString: '(KwH)'}}]},
        title: {display: true,text: 'Electricity Usage'}}});}});});

$(function () {var $rentChart = $("#tenantRentChart");
    $.ajax({url: $rentChart.data("url"),success: function (data) {
    var ctx = $rentChart[0].getContext("2d");
    new Chart(ctx, {type: 'line',data: {labels: data.labels,
        datasets: [{label: 'amount',backgroundColor: 'brown',data: data.data}]},
        options: {responsive: true,legend: {display: false,},scales: {
        yAxes: [{ticks: {display: false,beginAtZero: true}}]},
        title: {display: true,text: 'Rent Overview'}}});}});});

