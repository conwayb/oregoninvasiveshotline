/*
 * When a category is selected we need to remove any species from the species
 * drop down list that aren't in that category. Unfortunately, we can't just
 * use `display:none` on the <option> tags, since that doesn't work in all
 * browsers. If the category isn't selected, then hide the species drop down
 */
$(document).ready(function(){
    // keep a copy of the original list, since each time the category changes,
    // we need to restore the original, and remove the irrelevant items
    var original_list = $('#id_reported_species').html()
    $('body').on('change', '#id_reported_category', function(e){
        var category_id = $(this).val();
        if(category_id){
            $('#reported-species').show()
            $('#id_reported_species').html(original_list)

            var species_ids = category_id_to_species_id[category_id] || [];
            $('#id_reported_species option').each(function(i){
                // the first option is assumed to be the "Unknown" option,
                // which we always want to keep
                if(i == 0) return;
                // if the option isn't in our species_ids list, then we don't
                // want to show it
                if(species_ids.indexOf(parseInt($(this).val())) == -1){
                    $(this).remove()
                }
            });
        } else {
            $('#reported-species').hide()
        }
    });
    $('#id_reported_category').change()
});
