$(document).ready(function() {
    /*
	$el = $('#description_box');
	var desc_pos = $el.offset(); // Store the position here so we can return the box once top is reach
	
	$(window).scroll(function(e){ 
		if( $(this).scrollTop() > desc_pos.top && $el.css('position') != 'fixed' ){ 
			$el.css({'position': 'fixed', 'top': '0px'}); 
		} else if ( $(this).scrollTop() < desc_pos.top && $el.css('position') == 'fixed')  {
			$el.css({'position': 'relative'}); 
		}
	});
	*/
	var aucion_uri = '';
	$('.fund').click(function() {
		auction_uri = $(this).data('uri');
	});
	
	$('#fund_item').click(function(event) {
                event.preventDefault();
                var amount = $('input[name=option5]:checked', '#fund_form').attr('value');
                $.post(auction_uri, {'amount':amount}, function(data){
                    switch(data['error']){
                        case 'AUTH_REQUIRED': redirect("{% url acct_login %}"); break;
                        case 'NOT_ENOUGH_CREDITS': alert("/buycredits/"); break;
                        case 'ALREADY_HIGHEST_BID': alert('ALREADY_HIGHEST_BID'); break;
                        case 'AUCTION_EXPIRED': alert('AUCTION_EXPIRED'); break;
                        case 'AUCTION_IS_NOT_READY_YET': alert('AUCTION_IS_NOT_READY_YET'); break;
                    }
                    //window.location.reload();
                }, 'json');
                $('#fundModal').modal('hide');
                get_account_bids(function(data){
                    $('#member_bids').text(data);
                });
                update_item_ui();
                window.location.reload();
            });
	
	/* Quick sand sorting */
	var $items_container = $('#items');
	var $items_clone     = $items_container.clone(); // We sort this to do not break the original
	var $sorting         = $('.btn-group.sorting button');
		$sorting.click(function() {
			console.log('sorting by name');
			var $button = $(this);
			var $filteredData = $items_clone.find('li'); // Get all the items
			
			// Sort by name
			var $sortedData = $filteredData.sorted({
				by: function(v) {
				  return $(v).find('.fund-title').text().toLowerCase();
				}
			  });
			console.log($sortedData);
			 $items_container.quicksand($sortedData, {
			  	duration: 800,
			  	easing: 'easeInOutQuad'
			 });

		});
});

// Custom sorting plugin
(function($) {
    $.fn.sorted = function(customOptions) {
        var options = {
            reversed: false,
            by: function(a) { return a.text(); }
        };
        $.extend(options, customOptions);
        $data = $(this);
        arr = $data.get();
        arr.sort(function(a, b) {
            var valA = options.by($(a));
            var valB = options.by($(b));
            if (options.reversed) {
                return (valA < valB) ? 1 : (valA > valB) ? -1 : 0;
            } else {
                return (valA < valB) ? -1 : (valA > valB) ? 1 : 0;
            }
        });
        return $(arr);
    };
})(jQuery);
