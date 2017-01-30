(function(){
    var app = angular.module( "APIBeardDemo", ['ng'] );

    // function APIBeardFunction($http) {
    //     this.loadedBeards = $http.get("http://localhost:8000/loadedBeards");
    // }

    app.service("APIBeardService",
                ['$http', function APIBeardFunction($http) {
                    scope = this;

                    this.beards = [];

                    this.setBeards = function(beards) {
                        this.beards = beards;
                    };

                    this.getBeards = function() {
                        return this.beards;
                    };

                    this.fetchBeards = function(){
                        $http.get("http://localhost:8000/loadedBeards").then( function(data) {
                            scope.setBeards(data.data);
                        });
                    };
                }
                ]);
    // app.service("APIBeardService", ['$http', function() {}]);

    // app.service('APIBeardService',
    //             ['$http',
    //              function($http) {

    //              }]);

    app.controller(
        'PanelController',
        ["APIBeardService", function(APIBeardService) {
            this.tab = 2;

            this.selectTab = function(setTab) {
                this.tab = setTab;
                // TODO make it not hard coded
                if(this.tab === 1) {
                    APIBeardService.fetchBeards();
                };
            };

            this.isSelected = function(checkTab) {
                return this.tab === checkTab;
            };
        }]);

    app.controller(
        'loadedBeardsController',
        ['APIBeardService', function(APIBeardService) {
            this.APIBeardService = APIBeardService;
            // store = this;
            // this.beards = [];

            // this.loadBeards = function() {
            //     // TODO do if else statement somewhere so that loading beards is
            //     // text, and the beards are bullet points
            //     this.beards = ['Loading beards...'];
            //     $http.get("http://localhost:8000/loadedBeards").then(
            //         function(data) {
            //             store.beards = data.data;
            //         });
            // };
        }]);

    app.directive('loadedBeards', function(){
        return {
            restrict: "E",
            templateUrl: "loaded-beards.html"
        };
    });
})();                           // End of closure
