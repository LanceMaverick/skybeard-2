(function(){
    var app = angular.module( "APIBeardDemo", [] );
    app.controller(
        'APIBeardDemoController',
        ["$http",
         function($http) {
             this.result = "Click me to get info about beards.";

             var store = this;

             this.onClick = function() {
                 $http.get("http://localhost:8000/").then(function(data){
                     store.result = data;
                 });
             };

         }]);
})();                           // End of closure
