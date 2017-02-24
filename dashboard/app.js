(function(){
  var app = angular.module( "APIBeardDemo", ['ng'] );
  app.service(
    "APIBeardService",
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
    }]);

  app.directive('loadedBeards', function(){
    return {
      restrict: "E",
      templateUrl: "loaded-beards.html"
    };
  });
})();                           // End of closure
