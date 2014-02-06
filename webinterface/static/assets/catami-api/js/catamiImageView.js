function launchImageModal(requestedId) {           
    var requestedApiUrl = 'http://localhost:8000/api/dev/image/'+requestedId+'/?&format=json';
    var requestedIdAsInt = parseInt(requestedId,10); 
    var previousId = requestedIdAsInt - 1;
    var nextId = requestedIdAsInt + 1;
    
    $.ajax({
         async: true,
         url: requestedApiUrl,
         dataType: "json",
         success: function(jsonData) {
            var imageName = jsonData["web_location"].split("/").slice(-1)[0];
          
            $.fancybox({
                'autoScale': true,
                'transitionIn': 'elastic',
                'transitionOut': 'elastic',
                'speedIn': 100,
                'speedOut': 50,
                'autoDimensions': true,
                'centerOnScroll': true,
                'title': imageName,
                'href' : jsonData["web_location"],
                afterLoad: function(current, previous) {
                    console.info( 'Current: ' + 'peep' );        
                    console.info( 'Previous: ' +'poop' );
                }
        
            });               
            // $('#imageModal .modal-body').html("<div><div class='textOverlay'><h6>"+imageName+"</h6></div><img src='"+jsonData["web_location"]+"'></div>");
            // $('#imageModal .modal-footer').html("<a href='javascript:launchImageModal("+previousId+")' role='button' data-toggle='modal'><i class='icon-angle-left icon-4x pull-left'></i></a><a href='javascript:launchImageModal("+nextId+")'><i class='icon-angle-right icon-4x pull-right'></i></a>");
            // $('#imageModal').modal({show:true});
         }
    })                       
}

