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

    //////
    // set handlers
    $(".ResponsePrompt > .Yes").hover(
        function(){
            $(".Things > .ThenNo").animate({opacity:"0"}, 500, 'swing');
        },
        function(){
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

    var elems_to_eliminate = $($(".Eliminated").get().reverse()) ;    
    //disappear_in_sequence(elems_to_eliminate) ;

    //fadeout_and_disappear();
});
