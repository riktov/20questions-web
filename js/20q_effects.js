$(document).ready(function(){
    //console.log('Readyman') ;

    function set_block_side_length() {
        var num_elems = $('.Things').children().length ;
        var side_len = Math.ceil(Math.sqrt(num_elems)) ;
    
        console.log(side_len) ;
        $('.ThingsBlockContainer').css("width", side_len * 12).css("height", side_len * 12) ;
    }

    function disappear_in_sequence(elems) {
        if (elems.length < 1) {
            console.log("finished vanishing eliminated objects.") ;
	    update_in_sequence($(".Changed"));
            //$(".Changed").addClass('Animated').removeClass('Changed');
        }
        else {
            elems.first().animate(
                {width: "0"},
                70,
                'swing', 
                function() { 
                    this.remove();
                    disappear_in_sequence(elems.slice(1));
                }
            )
        }
    }

    function update_in_sequence(tiles) {
	      var interval = setInterval(
	          function() {
		            if (tiles.length < 1) {
		                clearInterval(interval) ;
		            } else {
		                tiles.first().addClass("Animated");
		                tiles = tiles.slice(1) ;
		            }
	          },
	          10) ;
				
	//tiles.first().delay(100).addClass("Animated");
	//update_in_sequence(tiles.slice(1));
    }

    //////
    // set handlers
    $(".ResponsePrompt > .Yes").hover(
        function(){
	    console.log("Entered Yes") ;
	    
	    //if(mouse_exited) {
		$(".Things > .ThenNo").animate({opacity:"0"}, 500, 'swing');
	    //}
        },
        function(){
	    //mouse_exited = true ;
            $(".Things > .ThenNo").animate({opacity:"1"}, 500, 'swing');
        });
        
    $(".ResponsePrompt > .No").hover(
        function(){
            $(".Things > .ThenYes").animate({opacity:"0"}, 500, 'swing');
        },
        function(){
            $(".Things > .ThenYes").animate({opacity:"1"}, 500, 'swing');
        });

    /////////////////////
    // main

    //$(".Eliminated").addClass('Animated');
    //first trigger the CSS-based transition
    //$(".Changed").addClass('Animated').removeClass('Changed');

    //elems_to_eliminate.removeClass('Animated') ;

//    var all_tiles = $("")

    var mouse_exited = false ;

    var tiles_to_eliminate = $($(".Eliminated").get().reverse()) ;

    disappear_in_sequence(tiles_to_eliminate) ;
    //$(".Things").css('opacity', 1.0);
    //fadeout_and_disappear();
});
